import sys
import re
import copy
import tkinter as tk
from tkinter import font
import random

class Color:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

# Token types and patterns for lexical analysis
TOKEN_SPECIFICATION = [
    ('DATATYPE',               r'\b(cycle|trace|canon)\b'), 
    ('OUTPUT_KEYWORD',         r'\b(observe)\b'),
    ('STATE_COMMAND',          r'\b(snapshot|revert|prune|premonition)\b'),
    ('CONTROL_KEYWORD',        r'\b(branch|bootstrap)\b'),
    ('CANON_LITERAL',          r'\b(fixed|erased)\b'),
    ('OOP_KEYWORD',            r'\b(entity|invoke)\b'),
    ('RETROCAUSAL_ASSIGNMENT', r'<<'),
    ('ANCHOR_DELIMITER',       r'@'),
    ('MATH_OPERATOR',          r'[+\-*/]'),
    ('LOGICAL_OPERATOR',       r'==|>|<|>=|<='),
    ('SCOPE_START',            r'\{'),
    ('SCOPE_END',              r'\}'),
    ('PAREN_START',            r'\('),
    ('PAREN_END',              r'\)'),
    ('NUMERIC_LITERAL',        r'\d+'),
    ('TRACE_LITERAL',          r'"[^"]*"'),               
    ('IDENTIFIER',             r'[A-Za-z_][A-Za-z0-9_]*'), 
    ('WHITESPACE',             r'\s+'),                   
    ('UNKNOWN',                r'.'),                     
]

def tokenize(code):
    # Performs lexical analysis: converts source code into tokens
    print(f"\n{Color.CYAN}{Color.BOLD}--- PHASE 1: INITIATING TEMPORAL SCAN (LEXICAL ANALYSIS) ---{Color.RESET}")
    tokens = []
    unknown_count = 0
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in TOKEN_SPECIFICATION)
    
    for match in re.finditer(tok_regex, code):
        kind = match.lastgroup
        value = match.group()
        
        if kind == 'WHITESPACE': continue 
        elif kind == 'UNKNOWN':
            unknown_count += 1
            print(f"{Color.YELLOW}[LEXER WARNING] Foreign artifact '{value}' detected. Skipping.{Color.RESET}")
        else:
            print(f"[LEXER] Found '{value}' -> Categorized as {Color.BOLD}{kind}{Color.RESET}")
            tokens.append((kind, value))
            
    if unknown_count == 0:
        print(f"\n{Color.GREEN}[SUCCESS] Lexical Analysis Complete.{Color.RESET}")
    return tokens


class Parser:
    # Syntax parser: validates token structure and grammar
    def __init__(self, token_stream):
        # Initialize parser with token stream
        self.tokens = token_stream

    def parse_assignment(self):
        # Validates assignment statement structure (datatype identifier << value @)
        if len(self.tokens) < 4 or self.tokens[2][0] != 'RETROCAUSAL_ASSIGNMENT': 
            print(f"{Color.RED}[PARSER ERROR] Invalid assignment structure.{Color.RESET}")
            return False
        if self.tokens[3][0] not in ['NUMERIC_LITERAL', 'TRACE_LITERAL', 'CANON_LITERAL']: 
            print(f"{Color.RED}[PARSER ERROR] Invalid literal assigned.{Color.RESET}")
            return False
        if len(self.tokens) == 4 or self.tokens[4][0] != 'ANCHOR_DELIMITER':
            print(f"{Color.RED}[PARSER ERROR] Missing anchor delimiter '@'.{Color.RESET}")
            return False
        
        print(f"{Color.GREEN}[PARSER] Structure verified.{Color.RESET}")
        return True

    def parse_state_command(self):
        # Validates state command structure (snapshot/revert/prune identifier @)
        if len(self.tokens) < 2: 
            print(f"{Color.RED}[PARSER ERROR] Incomplete state command.{Color.RESET}")
            return False
        if len(self.tokens) == 2 or self.tokens[2][0] != 'ANCHOR_DELIMITER':
            print(f"{Color.RED}[PARSER ERROR] Missing anchor delimiter '@'.{Color.RESET}")
            return False
        
        print(f"{Color.GREEN}[PARSER] State command structure verified.{Color.RESET}")
        return True
        
    def parse_branch(self):
        # Validates branch statement structure (branch @)
        if len(self.tokens) == 2 and self.tokens[0][1] == 'branch' and self.tokens[1][0] == 'ANCHOR_DELIMITER':
            print(f"{Color.GREEN}[PARSER] Branch scoping structure verified.{Color.RESET}")
            return True
        print(f"{Color.RED}[PARSER ERROR] Invalid branch syntax.{Color.RESET}")
        return False

    def parse_entity_declaration(self):
        # Validates entity blueprint declaration structure
        if len(self.tokens) < 9: 
            print(f"{Color.RED}[PARSER ERROR] Incomplete entity blueprint.{Color.RESET}")
            return False
        if self.tokens[0][0] != 'OOP_KEYWORD' or self.tokens[0][1] != 'entity': return False
        if self.tokens[1][0] != 'IDENTIFIER' or self.tokens[2][0] != 'SCOPE_START': return False
        if self.tokens[8][0] != 'SCOPE_END': 
            print(f"{Color.RED}[PARSER ERROR] Missing scope terminator '}}'.{Color.RESET}")
            return False
            
        print(f"{Color.GREEN}[PARSER] Entity blueprint structure verified.{Color.RESET}")
        return True

    def parse_instantiation(self):
        # Validates object instantiation structure (identifier identifier invoke classname @)
        if len(self.tokens) < 6: 
            print(f"{Color.RED}[PARSER ERROR] Incomplete object instantiation.{Color.RESET}")
            return False
        if self.tokens[3][0] != 'OOP_KEYWORD' or self.tokens[3][1] != 'invoke': return False
        if len(self.tokens) == 5 or self.tokens[5][0] != 'ANCHOR_DELIMITER':
            print(f"{Color.RED}[PARSER ERROR] Missing anchor delimiter '@'.{Color.RESET}")
            return False
            
        print(f"{Color.GREEN}[PARSER] Object instantiation structure verified.{Color.RESET}")
        return True

    def parse_bootstrap(self):
        # Validates bootstrap loop structure with condition and assignment
        if len(self.tokens) < 16: 
            print(f"{Color.RED}[PARSER ERROR] Incomplete bootstrap loop.{Color.RESET}")
            return False
        if self.tokens[0][0] != 'CONTROL_KEYWORD' or self.tokens[0][1] != 'bootstrap': return False
        if len(self.tokens) == 15 or self.tokens[15][0] != 'ANCHOR_DELIMITER':
            print(f"{Color.RED}[PARSER ERROR] Missing anchor delimiter '@' after origin.{Color.RESET}")
            return False
            
        print(f"{Color.GREEN}[PARSER] Bootstrap loop structure verified.{Color.RESET}")
        return True

    def parse_observe(self):
        # Validates observe statement structure (observe identifier @)
        if len(self.tokens) < 2: 
            print(f"{Color.RED}[PARSER ERROR] Incomplete observe statement.{Color.RESET}")
            return False
        if len(self.tokens) == 2 or self.tokens[2][0] != 'ANCHOR_DELIMITER':
            print(f"{Color.RED}[PARSER ERROR] Missing anchor delimiter '@'.{Color.RESET}")
            return False
            
        print(f"{Color.GREEN}[PARSER] Output statement structure verified.{Color.RESET}")
        return True

class SemanticAnalyzer:
    # Semantic analyzer: manages variable binding, scoping, and execution
    def __init__(self):
        # Initialize symbol table, snapshots, and scope tracking
        self.symbol_table = {}
        self.snapshots = {} 
        self.entities = {}
        self.last_observed = None
        
        self.current_level = 0
        self.level_offsets = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
        
        self.byte_sizes = {
            'cycle': 4,   
            'trace': 1,   
            'canon': 1,   
            'Obj': 8      
        }

    def analyze_assignment(self, tokens):
        # Binds variables to symbol table with type and scope information
        datatype, identifier = tokens[0][1], tokens[1][1]    
        literal_type, literal_value = tokens[3][0], tokens[3][1] 
        type_map = {'cycle': 'NUMERIC_LITERAL', 'trace': 'TRACE_LITERAL', 'canon': 'CANON_LITERAL'}
        
        if type_map.get(datatype) == literal_type:
            if identifier not in self.symbol_table:
                offset = self.level_offsets[self.current_level]
                
                self.symbol_table[identifier] = {
                    'type': datatype, 
                    'value': literal_value, 
                    'level': self.current_level, 
                    'offset': offset
                }
                self.level_offsets[self.current_level] += self.byte_sizes[datatype]
            else:
                self.symbol_table[identifier]['value'] = literal_value
                self.symbol_table[identifier]['type'] = datatype
                
            print(f"[SEMANTICS] {Color.GREEN}SUCCESS:{Color.RESET} Binding '{identifier}' to Symbol Table at Level {self.current_level}.")
            return True
        else:
            print(f"{Color.RED}[FATAL PARADOX] Type Mismatch! '{identifier}' rejected.{Color.RESET}")
            return False

    def execute_branch(self, tokens):
        # Creates a new scope level for nested code blocks
        self.current_level += 1
        self.level_offsets[self.current_level] = 0 
        print(f"[SEMANTICS] {Color.CYAN}TIMELINE BRANCHED:{Color.RESET} Now operating at Scope Level {self.current_level}.")
        return True

    def execute_state_command(self, tokens):
        # Executes snapshot, revert, and prune timeline commands
        command, target = tokens[0][1], tokens[1][1]
        
        if command == 'snapshot':
            self.snapshots[target] = {
                'memory': copy.deepcopy(self.symbol_table),
                'levels': copy.deepcopy(self.level_offsets)
            }
            print(f"[SEMANTICS] {Color.GREEN}SNAPSHOT SUCCESS:{Color.RESET} Archiving timeline to '{target}'.")
            return True
            
        elif command == 'revert':
            if target in self.snapshots:
                self.symbol_table = copy.deepcopy(self.snapshots[target]['memory'])
                self.level_offsets = copy.deepcopy(self.snapshots[target]['levels'])
                print(f"[SEMANTICS] {Color.GREEN}REVERT SUCCESS:{Color.RESET} Restoring timeline to '{target}'.")
                return True
            else:
                print(f"{Color.RED}[FATAL PARADOX] Snapshot '{target}' not found.{Color.RESET}")
                return False
                
        elif command == 'prune':
            if target == 'branch':
                self.current_level = max(0, self.current_level - 1)
                print(f"[SEMANTICS] {Color.YELLOW}PRUNE COMMAND:{Color.RESET} Collapsing branch. Returning to Scope Level {self.current_level}.")
                return True
            
            if target in self.symbol_table:
                del self.symbol_table[target]
                print(f"[SEMANTICS] {Color.YELLOW}PRUNE COMMAND DETECTED:{Color.RESET} Erasing '{target}' from the timeline.")
                return True
            else:
                print(f"{Color.RED}[FATAL PARADOX] Target '{target}' not found in timeline.{Color.RESET}")
                return False
        return False

    def analyze_entity_declaration(self, tokens):
        # Registers entity (class) blueprints with properties
        entity_name = tokens[1][1]
        self.entities[entity_name] = {'prop_type': tokens[3][1], 'prop_name': tokens[4][1], 'prop_val': tokens[6][1]}
        print(f"[SEMANTICS] {Color.GREEN}SUCCESS:{Color.RESET} Entity blueprint '{entity_name}' saved.")
        return True

    def analyze_instantiation(self, tokens):
        # Creates objects from entity blueprints and binds them to symbol table
        class_name, obj_name, invoked_class = tokens[0][1], tokens[1][1], tokens[4][1]
        
        if class_name != invoked_class or class_name not in self.entities:
            print(f"{Color.RED}[FATAL PARADOX] Blueprint '{class_name}' error.{Color.RESET}")
            return False

        blueprint = self.entities[class_name]
        
        offset = self.level_offsets[self.current_level]
        self.symbol_table[obj_name] = {
            'type': f"Obj<{class_name}>",
            'value': f"{{ {blueprint['prop_name']}: {blueprint['prop_val']} }}",
            'level': self.current_level,
            'offset': offset
        }
        self.level_offsets[self.current_level] += self.byte_sizes['Obj']
        print(f"[SEMANTICS] {Color.GREEN}SUCCESS:{Color.RESET} Binding object '{obj_name}' to Symbol Table.")
        return True

    def analyze_bootstrap(self, tokens):
        # Executes temporal loops: iterates while condition is met and performs arithmetic
        print(f"[SEMANTICS] Initiating bootstrap loop sequence...")
        cond_var, cond_op, cond_val_token = tokens[2][1], tokens[3][1], tokens[4]
        assign_target, math_left, math_op, math_right_token = tokens[7][1], tokens[9][1], tokens[10][1], tokens[11]

        if cond_var not in self.symbol_table: 
            print(f"{Color.RED}[FATAL PARADOX] Loop condition variable '{cond_var}' not found in timeline.{Color.RESET}")
            return False

        cycle_count = 1
        while True:
            left_val = int(self.symbol_table[cond_var]['value'])
            cond_compare_val = int(cond_val_token[1]) if cond_val_token[0] == 'NUMERIC_LITERAL' else int(self.symbol_table[cond_val_token[1]]['value'])
            
            condition_met = (left_val > cond_compare_val) if cond_op == '>' else (left_val < cond_compare_val) if cond_op == '<' else (left_val == cond_compare_val)
            
            if not condition_met:
                print(f"[SEMANTICS] {Color.YELLOW}Cycle {cycle_count}: Loop condition failed. Breaking temporal loop.{Color.RESET}")
                break
                
            print(f"[SEMANTICS] Cycle {cycle_count}: Origin condition met.")
            m_left_val = int(self.symbol_table[math_left]['value']) if math_left in self.symbol_table else int(math_left)
            m_right_val = int(math_right_token[1]) if math_right_token[0] == 'NUMERIC_LITERAL' else int(self.symbol_table[math_right_token[1]]['value'])
            
            new_val = m_left_val + m_right_val if math_op == '+' else m_left_val - m_right_val if math_op == '-' else m_left_val * m_right_val
            self.symbol_table[assign_target]['value'] = str(new_val)
            print(f"[SEMANTICS] Binding new value '{new_val}' to '{assign_target}'.")
            
            cycle_count += 1
            if cycle_count > 20: break
        return True

    def analyze_observe(self, tokens):
        # Outputs the value of a variable to the terminal
        target = tokens[1][1]
        
        if target in self.symbol_table:
            print(f"[SEMANTICS] {Color.GREEN}OBSERVATION SUCCESS:{Color.RESET} Manifesting '{target}'.")
            print(f"\n{Color.BOLD}>> TERMINAL OUTPUT: {self.symbol_table[target]['value']}{Color.RESET}\n")
            self.last_observed = target 
            return True
        else:
            print(f"{Color.RED}[FATAL PARADOX] Target '{target}' not found in timeline.{Color.RESET}")
            return False


class TerminalRedirector:
    # Redirects print output to GUI text widget with ANSI color support
    def __init__(self, text_widget):
        # Initialize text widget and ANSI color mappings
        self.text_widget = text_widget
        
        
        self.text_widget.tag_config("CYAN", foreground="#00f0ff")
        self.text_widget.tag_config("GREEN", foreground="#00ff66")
        self.text_widget.tag_config("YELLOW", foreground="#ffe600")
        self.text_widget.tag_config("RED", foreground="#ff003c")
        self.text_widget.tag_config("BOLD", font=("Consolas", 11, "bold"))

        
        self.ansi_mapping = {
            '\033[96m': 'CYAN',
            '\033[92m': 'GREEN',
            '\033[93m': 'YELLOW',
            '\033[91m': 'RED',
            '\033[1m':  'BOLD'
        }
        
        
        self.ansi_regex = re.compile(r'(\033\[[0-9;]*m)')

    def write(self, str_data):
        # Writes text to widget with ANSI color code parsing and rendering
        if not self.text_widget.winfo_exists(): return
        self.text_widget.configure(state='normal')

        
        parts = self.ansi_regex.split(str_data)
        current_tags = [] 
        
        for part in parts:
            if part in self.ansi_mapping:
                tag = self.ansi_mapping[part]
                if tag not in current_tags:
                    current_tags.append(tag)
            elif part == '\033[0m': 
                current_tags = [] 
            elif part: 
                self.text_widget.insert(tk.END, part, tuple(current_tags))

        self.text_widget.see(tk.END) 
        self.text_widget.configure(state='disabled')

    def flush(self): pass
       

class ParadoxUI:
    # Main GUI application for PARADOX temporal programming environment
    def __init__(self, root):
        # Initialize window, theme, and display start menu
        self.root = root
        self.root.title("PARADOX")
        self.root.geometry("1200x850")
        self.root.minsize(900, 700)
        self.root.configure(bg="#030712") 

        self.semantics = SemanticAnalyzer()
        self.mission_stage = 1
        
        self.timeline_state = "fractured"
        self.degradation_level = 88 
        self.mode = None 
        
        self.show_start_menu()

    def show_start_menu(self):
        # Displays main menu with mode selection (Story/Sandbox)
        self.start_frame = tk.Frame(self.root, bg="#030712")
        self.start_frame.pack(expand=True, fill=tk.BOTH)

        title = tk.Label(self.start_frame, text="PARADOX Temporal Programming", bg="#030712", fg="#00f0ff", font=("Consolas", 56, "bold"))
        title.pack(pady=(150, 10))

        subtitle = tk.Label(self.start_frame, text="CS0035 - FINAL PROJECT", bg="#030712", fg="#4d6b99", font=("Consolas", 16))
        subtitle.pack(pady=(0, 60))

        btn_story = tk.Button(self.start_frame, text="[ INITIATE PROTOCOL : STORY MODE ]", bg="#050a14", fg="#ff003c", 
                              font=("Consolas", 16, "bold"), relief=tk.FLAT, highlightbackground="#ff003c", highlightthickness=2, 
                              activebackground="#ff003c", activeforeground="#ffffff", cursor="hand2",
                              command=lambda: self.launch_app("story"))
        btn_story.pack(pady=15, ipadx=30, ipady=15)

        btn_sandbox = tk.Button(self.start_frame, text="[ MANUAL OVERRIDE : SANDBOX MODE ]", bg="#050a14", fg="#00ff66", 
                                font=("Consolas", 16, "bold"), relief=tk.FLAT, highlightbackground="#00ff66", highlightthickness=2, 
                                activebackground="#00ff66", activeforeground="#000000", cursor="hand2",
                                command=lambda: self.launch_app("sandbox"))
        btn_sandbox.pack(pady=15, ipadx=30, ipady=15)

    def launch_app(self, selected_mode):
        # Initializes application UI and starts selected mode (story or sandbox)
        self.mode = selected_mode
        self.start_frame.destroy() 
        
        self.app_frame = tk.Frame(self.root, bg="#030712")
        self.app_frame.pack(expand=True, fill=tk.BOTH)
        
        self.setup_ui()
        sys.stdout = TerminalRedirector(self.console_output)
        
        print(f"=== {Color.CYAN}CHRONOS WEAVER OS INITIALIZED{Color.RESET} ===")
        
        if self.mode == "story":
            print(f"{Color.YELLOW}WARNING: Rogue agent detected. Reality anchors failing.{Color.RESET}")
            print(f"{Color.YELLOW}Initiate full spectrum containment protocol immediately.{Color.RESET}\n")
            self.timeline_state = "fractured"
            self.mission_stage = 1
            self.flash_warnings()
            self.system_warnings() 
            self.load_mission()
        elif self.mode == "sandbox":
            print(f"{Color.GREEN}SANDBOX MODE ACTIVE. No temporal threats detected.{Color.RESET}")
            print(f"{Color.GREEN}Awaiting standard compiler inputs. Panic events disabled.{Color.RESET}\n")
            self.timeline_state = "stable"
            self.stability_label.config(text="[ TIMELINE STABLE ]", fg="#00ff66")
            self.mission_frame.config(highlightbackground="#00ff66")
            self.mission_text.config(text="SANDBOX MODE ACTIVE. Freely test temporal programming constructs.")
            
        self.animate_timeline()

    def return_to_menu(self):
        # Clears application state and returns to main menu
        self.mode = None
        self.app_frame.destroy()
        
        self.semantics = SemanticAnalyzer()
        self.mission_stage = 1
        self.timeline_state = "fractured"
        self.degradation_level = 88
        
        self.show_start_menu()

    def setup_ui(self):
        # Constructs main application layout with all UI panels and text areas
        self.app_frame.columnconfigure(0, weight=1)
        self.app_frame.rowconfigure(0, weight=0) 
        self.app_frame.rowconfigure(1, weight=0) 
        self.app_frame.rowconfigure(2, weight=1) 
        self.app_frame.rowconfigure(3, weight=8) 
        self.app_frame.rowconfigure(4, weight=0) 

        custom_font = font.Font(family="Consolas", size=11)
        title_font = font.Font(family="Consolas", size=12, weight="bold")
        header_font = font.Font(family="Consolas", size=14, weight="bold")
        
        header_bar = tk.Frame(self.app_frame, bg="#030712")
        header_bar.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 0))
        
        self.back_btn = tk.Button(header_bar, text="[ < MAIN MENU ]", bg="#050a14", fg="#4d6b99", font=title_font, relief=tk.FLAT, bd=0, padx=10, cursor="hand2", command=self.return_to_menu)
        self.back_btn.pack(side=tk.LEFT)
        
        self.sys_reset_btn = tk.Button(header_bar, text="[ SYS.RESET ]", bg="#ff003c", fg="#ffffff", font=title_font, relief=tk.FLAT, bd=0, padx=10, cursor="hand2", command=self.reset_system)
        self.sys_reset_btn.pack(side=tk.RIGHT)

        self.mission_frame = tk.Frame(self.app_frame, bg="#081021", highlightbackground="#00f0ff", highlightthickness=1)
        self.mission_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=15)
        
        top_mission_bar = tk.Frame(self.mission_frame, bg="#081021")
        top_mission_bar.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(top_mission_bar, text="// CURRENT DIRECTIVE //", bg="#081021", fg="#00f0ff", font=header_font).pack(side=tk.LEFT)
        self.stability_label = tk.Label(top_mission_bar, text="[ TIMELINE FRACTURED ]", bg="#081021", fg="#ff003c", font=title_font)
        self.stability_label.pack(side=tk.RIGHT)
        
        self.mission_text = tk.Label(self.mission_frame, text="", bg="#081021", fg="#e0e0e0", font=custom_font, justify=tk.LEFT, wraplength=900)
        self.mission_text.pack(anchor="w", padx=15, pady=(0, 15))

        middle_pane = tk.Frame(self.app_frame, bg="#030712")
        middle_pane.grid(row=2, column=0, sticky="nsew", padx=20, pady=5)
        middle_pane.columnconfigure(0, weight=3) 
        middle_pane.columnconfigure(1, weight=2) 
        middle_pane.rowconfigure(0, weight=1)

        visual_frame = tk.Frame(middle_pane, bg="#030712")
        visual_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        tk.Label(visual_frame, text="TIMELINE VISUALIZER", bg="#030712", fg="#4d6b99", font=title_font).pack(anchor="w", pady=(0, 5))
        self.canvas = tk.Canvas(visual_frame, bg="#050a14", highlightbackground="#223355", highlightthickness=1)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        memory_frame = tk.Frame(middle_pane, bg="#030712")
        memory_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        tk.Label(memory_frame, text="UNIVERSAL SYMBOL TABLE", bg="#030712", fg="#ffe600", font=title_font).pack(anchor="w", pady=(0, 5))
        
        self.memory_display = tk.Text(memory_frame, width=40, height=6, bg="#050a14", fg="#00f0ff", font=custom_font, relief=tk.FLAT, highlightbackground="#223355", highlightthickness=1)
        self.memory_display.pack(fill=tk.BOTH, expand=True)
        self.update_memory_ui()

        bottom_frame = tk.Frame(self.app_frame, bg="#030712")
        bottom_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=(15, 5))
        bottom_frame.rowconfigure(1, weight=1)
        bottom_frame.columnconfigure(0, weight=1)

        tk.Label(bottom_frame, text="PARADOX COMPILER CONSOLE", bg="#030712", fg="#4d6b99", font=title_font).grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.console_output = tk.Text(bottom_frame, bg="#000000", fg="#00ff66", font=custom_font, relief=tk.FLAT, highlightbackground="#223355", highlightthickness=1, state='disabled')
        self.console_output.grid(row=1, column=0, sticky="nsew")

        input_frame = tk.Frame(self.app_frame, bg="#030712")
        input_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=(5, 20))
        input_frame.columnconfigure(1, weight=1)
        
        tk.Label(input_frame, text="Paradox > ", bg="#030712", fg="#ffe600", font=header_font).grid(row=0, column=0, sticky="nw", pady=5)
        
        self.command_input = tk.Text(input_frame, bg="#081021", fg="#ffffff", font=("Consolas", 13), insertbackground="#00f0ff", relief=tk.FLAT, highlightbackground="#223355", highlightthickness=1, height=4)
        self.command_input.grid(row=0, column=1, sticky="ew", pady=5, padx=(0, 10))
        
        self.execute_btn = tk.Button(input_frame, text="[ EXECUTE ]\n[ SCRIPT ]", bg="#00f0ff", fg="#000000", font=("Consolas", 12, "bold"), relief=tk.FLAT, cursor="hand2", command=self.process_script)
        self.execute_btn.grid(row=0, column=2, sticky="ns", pady=5)

    def system_warnings(self):
        # Generates periodic system warning messages based on mission stage
        if self.mode == "sandbox" or self.mode is None: return
        if not hasattr(self, 'console_output') or not self.console_output.winfo_exists(): return

        delay = 3000
        warnings = []
        
        if self.mission_stage == 1:
            self.degradation_level = min(99, self.degradation_level + random.randint(1, 4))
            warnings = ["[SYS_ERR] CHRONO-CORE COLLAPSE IMMINENT...", f"[ALERT] REALITY ANCHORS FAILING! DEGRADATION AT {self.degradation_level}%"]
            delay = random.randint(1500, 2500)
        elif self.mission_stage == 2:
            self.degradation_level = max(70, self.degradation_level - random.randint(1, 3))
            warnings = ["[SYS_ERR] VANGUARD COMMS OFFLINE. SOS REQUIRED.", f"[ALERT] DEGRADATION CURRENTLY AT {self.degradation_level}%"]
            delay = random.randint(2500, 3500)
        elif self.mission_stage == 3:
            self.degradation_level = max(55, self.degradation_level - random.randint(2, 4))
            warnings = ["[INFO] SOS BEACON BROADCASTING.", "[SYS_ERR] NO TEMPORAL SNAPSHOT ANCHOR DETECTED."]
            delay = random.randint(3000, 4500)
        elif self.mission_stage == 4:
            self.degradation_level = min(95, self.degradation_level + random.randint(5, 15))
            warnings = ["[CRITICAL] MEMORY CORRUPTION DETECTED IN SYMBOL TABLE!", f"[ALERT] CASCADING FAILURE AT {self.degradation_level}% - EXCISE IMMEDIATELY!"]
            delay = random.randint(1000, 2000)
        elif self.mission_stage == 5:
            self.degradation_level = max(40, self.degradation_level - random.randint(5, 10))
            warnings = ["[INFO] CORRUPTION PURGED. CORE OFFLINE.", "[WARN] AWAITING TEMPORAL REVERSION..."]
            delay = random.randint(4000, 6000)
        elif self.mission_stage == 6:
            self.degradation_level = max(30, self.degradation_level - random.randint(1, 4))
            warnings = ["[INFO] CORE RESTORED. SNAPSHOT ANCHOR SECURED.", "[WARN] ANOMALY RESIDUE STILL PRESENT. REJECT IT."]
            delay = random.randint(4000, 6000)
        elif self.mission_stage == 7:
            self.degradation_level = max(20, self.degradation_level - random.randint(1, 3))
            warnings = ["[INFO] ANOMALY CLASSIFIED AS FALSE. WEAKENING...", "[WARN] PARADOX RADIATION INCREASING. CONTAINMENT FIELD REQUIRED."]
            delay = random.randint(5000, 6000)

        if warnings and self.mission_stage < 10:
            # Let the Redirector handle the UI color injection
            print(f"{Color.RED}{random.choice(warnings)}{Color.RESET}\n")
        
        self.root.after(delay, self.system_warnings)

    def flash_warnings(self):
        # Animates border color flashing based on timeline stability state
        if self.mode == "sandbox" or self.mode is None: return
        if not hasattr(self, 'mission_frame') or not self.mission_frame.winfo_exists(): return

        if self.timeline_state in ["fractured", "critical"]:
            current_color = self.stability_label.cget("fg")
            next_color = "#ffffff" if current_color == "#ff003c" else "#ff003c"
            self.stability_label.config(fg=next_color)
            self.mission_frame.config(highlightbackground=next_color)
            self.root.after(300, self.flash_warnings)
        elif self.timeline_state == "unstable":
            current_color = self.stability_label.cget("fg")
            next_color = "#ffffff" if current_color == "#ffaa00" else "#ffaa00"
            self.stability_label.config(fg=next_color)
            self.mission_frame.config(highlightbackground=next_color)
            self.root.after(800, self.flash_warnings)
        elif self.timeline_state == "recovering":
            self.stability_label.config(fg="#ffe600")
            self.mission_frame.config(highlightbackground="#ffe600")
            self.root.after(1000, self.flash_warnings)
        else:
            self.mission_frame.config(highlightbackground="#00f0ff")

    def draw_timeline(self):
        # Renders timeline visualization with state-dependent graphics
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width < 10: width, height = 400, 150
        mid_y = height // 2

        for i in range(0, width, 40): self.canvas.create_line(i, 0, i, height, fill="#0d1b2a", dash=(2, 4))
        for i in range(0, height, 40): self.canvas.create_line(0, i, width, i, fill="#0d1b2a", dash=(2, 4))
        
        if self.timeline_state in ["fractured", "unstable", "critical", "recovering"]:
            color = "#ff003c" if self.timeline_state in ["fractured", "critical"] else "#ffaa00" if self.timeline_state == "unstable" else "#ffe600"
            intensity = 90 if self.timeline_state == "critical" else 70 if self.timeline_state == "fractured" else 40 if self.timeline_state == "unstable" else 20
            
            for _ in range(25):
                x1, y1 = random.randint(0, width), mid_y + random.randint(-intensity, intensity)
                x2, y2 = x1 + random.randint(-40, 40), y1 + random.randint(-40, 40)
                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=random.randint(1, 3))
            
            points = []
            for x in range(0, width + 30, 30):
                offset = random.randint(-intensity, intensity) if self.timeline_state in ["fractured", "critical"] else random.randint(-20, 20)
                points.extend([x, mid_y + offset])
            self.canvas.create_line(points, fill="#ffffff", width=2, dash=(2, 4))

        elif self.timeline_state == "offline":
            self.canvas.create_line(0, mid_y, width, mid_y, fill="#ff003c", width=2)

        elif self.timeline_state == "shielded":
            self.canvas.create_rectangle(0, mid_y - 20, width, mid_y + 20, outline="#00f0ff", width=2, dash=(5, 5))
            points = []
            for x in range(0, width + 30, 30):
                offset = random.randint(-10, 10)
                points.extend([x, mid_y + offset])
            self.canvas.create_line(points, fill="#00f0ff", width=4)

        elif self.timeline_state == "stable":
            self.canvas.create_line(0, mid_y, width, mid_y, fill="#00f0ff", width=6)
            self.canvas.create_line(0, mid_y, width, mid_y, fill="#ffffff", width=2)

    def animate_timeline(self):
        # Continuously redraws timeline at intervals based on system state
        if self.mode is None: return
        if not hasattr(self, 'canvas') or not self.canvas.winfo_exists(): return
        
        self.draw_timeline()
        speed = 50 if self.timeline_state == "critical" else 80 if self.timeline_state in ["fractured", "unstable"] else 120 if self.timeline_state == "recovering" else 200
        self.root.after(speed, self.animate_timeline)


    def process_script(self):
        # Tokenizes, parses, and semantically analyzes user code input
        source_code = self.command_input.get("1.0", tk.END).strip()
        if not source_code: return
        self.command_input.delete("1.0", tk.END)
        
        print(f"\nParadox > Executing Script Block...")

        token_stream = tokenize(source_code)
        if not token_stream: return
        
        raw_statements = []
        temp_stream = list(token_stream)
        while temp_stream:
            first_token_type = temp_stream[0][0]
            first_val = temp_stream[0][1]
            end_idx = -1

            if first_token_type == 'OOP_KEYWORD' and first_val == 'entity':
                end_idx = next((i for i, tok in enumerate(temp_stream) if tok[0] == 'SCOPE_END'), -1)
            elif first_token_type == 'CONTROL_KEYWORD' and first_val == 'bootstrap':
                origin_idx = next((i for i, tok in enumerate(temp_stream) if tok[1] == 'origin'), -1)
                if origin_idx != -1 and origin_idx + 1 < len(temp_stream) and temp_stream[origin_idx+1][0] == 'ANCHOR_DELIMITER':
                    end_idx = origin_idx + 1
                else:
                    end_idx = origin_idx
            else:
                end_idx = next((i for i, tok in enumerate(temp_stream) if tok[0] == 'ANCHOR_DELIMITER'), -1)

            if end_idx == -1:
                starting_keywords = ['DATATYPE', 'STATE_COMMAND', 'OOP_KEYWORD', 'CONTROL_KEYWORD', 'OUTPUT_KEYWORD', 'IDENTIFIER']
                next_start = next((i for i, tok in enumerate(temp_stream[1:], 1) if tok[0] in starting_keywords), len(temp_stream))
                end_idx = next_start - 1

            statement_tokens = temp_stream[:end_idx + 1]
            temp_stream = temp_stream[end_idx + 1:]
            raw_statements.append(statement_tokens)

        
        for statement_tokens in raw_statements:
            
            
            parser = Parser(statement_tokens)
            st_type = statement_tokens[0][0]
            is_valid = False
            
            if st_type == 'DATATYPE': is_valid = parser.parse_assignment()
            elif st_type == 'STATE_COMMAND': is_valid = parser.parse_state_command()
            elif st_type == 'CONTROL_KEYWORD' and statement_tokens[0][1] == 'branch': is_valid = parser.parse_branch()
            elif st_type == 'OOP_KEYWORD' and statement_tokens[0][1] == 'entity': is_valid = parser.parse_entity_declaration()
            elif st_type == 'IDENTIFIER': is_valid = parser.parse_instantiation()
            elif st_type == 'CONTROL_KEYWORD' and statement_tokens[0][1] == 'bootstrap': is_valid = parser.parse_bootstrap()
            elif st_type == 'OUTPUT_KEYWORD' and statement_tokens[0][1] == 'observe': is_valid = parser.parse_observe()
            else: 
                print(f"\n{Color.CYAN}{Color.BOLD}--- PHASE 2: VERIFYING TIMELINE STRUCTURE (SYNTAX ANALYSIS) ---{Color.RESET}")
                print(f"{Color.RED}[PARSER ERROR] Invalid syntax or routing failed.{Color.RESET}")
                is_valid = False

            
            if not is_valid:
                print(f"\n{Color.RED}[FATAL ERROR] Syntax Violation. Compilation Aborted. Symbol Table generation halted.{Color.RESET}\n")
                return 

            
            success = False
            if st_type == 'DATATYPE': success = self.semantics.analyze_assignment(statement_tokens)
            elif st_type == 'STATE_COMMAND': success = self.semantics.execute_state_command(statement_tokens)
            elif st_type == 'CONTROL_KEYWORD' and statement_tokens[0][1] == 'branch': success = self.semantics.execute_branch(statement_tokens)
            elif st_type == 'OOP_KEYWORD': success = self.semantics.analyze_entity_declaration(statement_tokens)
            elif st_type == 'IDENTIFIER': success = self.semantics.analyze_instantiation(statement_tokens)
            elif st_type == 'CONTROL_KEYWORD' and statement_tokens[0][1] == 'bootstrap': success = self.semantics.analyze_bootstrap(statement_tokens)
            elif st_type == 'OUTPUT_KEYWORD': success = self.semantics.analyze_observe(statement_tokens)

            
            if not success:
                print(f"\n{Color.RED}[FATAL ERROR] Semantic Violation. Execution Aborted. Symbol Table generation halted.{Color.RESET}\n")
                self.update_memory_ui()
                return 

        self.update_memory_ui()
        if self.mode == "story":
            self.check_mission_progress()

    def load_mission(self):
        # Loads and displays mission objectives and timeline status
        if self.mode == "sandbox": return

        missions = {
            1: ("A rogue agent erased a historical figure. The timeline is fracturing!\n[TASK] Initialize the core: Bind a cycle variable named 'energy' to 50.", "FRACTURED"),
            2: ("We must warn the Temporal Vanguard before communications go down.\n[TASK] Send a distress signal: Bind a trace variable named 'beacon' to \"SOS\".", "UNSTABLE"),
            3: ("We need to anchor this broken state before the anomaly spreads.\n[TASK] Save the fractured timeline: Create a snapshot named \"Fracture\".", "UNSTABLE"),
            4: ("[ALERT] The anomaly is corrupting the energy variable! We must excise it.\n[TASK] Prune the variable: Type 'prune energy @'.", "CRITICAL"),
            5: ("[ALERT] Core power depleted! System offline. We need that energy back.\n[TASK] Time travel: Restore the timeline by typing 'revert \"Fracture\" @'.", "OFFLINE"),
            6: ("Core restored. Now, forcefully deny the anomaly's existence to weaken it.\n[TASK] Reject the paradox: Bind a canon variable named 'paradox' to erased.", "UNSTABLE"),
            7: ("The paradox is weakened! Quickly, build a containment shield.\n[TASK] Design the shield: Create an entity blueprint named 'Shield' with a canon property 'active' set to 'fixed'.", "RECOVERING"),
            8: ("Deploy the containment shield around the timeline!\n[TASK] Deploy the shield: Instantiate a Shield object named 'aegis' using invoke.", "RECOVERING"),
            9: ("The shield is deployed. Verify its structural integrity before the purge.\n[TASK] Inspect the shield: Type 'observe aegis @'.", "SHIELDED"),
            10: ("Integrity confirmed. Purge the remaining temporal decay. Reverse the flow!\n[TASK] Run a Chronomath loop: Use bootstrap to loop while (energy > 0), re-assigning energy to (energy - 10).", "SHIELDED"),
            11: ("PARADOX CONTAINED. TIMELINE SECURE. EXCELLENT WORK.\n[SANDBOX MODE UNLOCKED]", "SECURE")
        }
        
        mission_data = missions.get(self.mission_stage, ("Sandbox Mode Active. Awaiting standard terminal inputs.", "SECURE"))
        self.mission_text.config(text=mission_data[0])
        self.stability_label.config(text=f"[ STATUS: {mission_data[1]} ]")
        
        if self.mission_stage in [1, 4]: self.stability_label.config(fg="#ff003c") 
        elif self.mission_stage == 5: self.stability_label.config(fg="#ff003c") 
        elif self.mission_stage in [2, 3, 6]: self.stability_label.config(fg="#ffaa00") 
        elif self.mission_stage in [7, 8]: self.stability_label.config(fg="#ffe600") 
        elif self.mission_stage in [9, 10]: self.stability_label.config(fg="#00f0ff") 
        else: self.stability_label.config(fg="#00ff66") 

    def check_mission_progress(self):
        # Verifies mission objectives and advances to next stage if completed
        if self.mission_stage == 1 and "energy" in self.semantics.symbol_table and self.semantics.symbol_table["energy"]["value"] == "50":
            self.timeline_state = "unstable"
            self.advance_mission(2)
            self.flash_warnings() 
        elif self.mission_stage == 2 and "beacon" in self.semantics.symbol_table and self.semantics.symbol_table["beacon"]["value"] == '"SOS"':
            self.advance_mission(3)
        elif self.mission_stage == 3 and '"Fracture"' in self.semantics.snapshots:
            self.timeline_state = "critical"
            self.advance_mission(4)
            self.flash_warnings()
        elif self.mission_stage == 4 and "energy" not in self.semantics.symbol_table:
            self.timeline_state = "offline"
            self.advance_mission(5)
        elif self.mission_stage == 5 and "energy" in self.semantics.symbol_table:
            self.timeline_state = "unstable"
            self.advance_mission(6)
            self.flash_warnings()
        elif self.mission_stage == 6 and "paradox" in self.semantics.symbol_table and self.semantics.symbol_table["paradox"]["value"] == "erased":
            self.timeline_state = "recovering"
            self.advance_mission(7)
            self.flash_warnings()
        elif self.mission_stage == 7 and "Shield" in self.semantics.entities:
            self.advance_mission(8)
        elif self.mission_stage == 8 and "aegis" in self.semantics.symbol_table:
            self.timeline_state = "shielded"
            self.stability_label.config(fg="#00f0ff")
            self.mission_frame.config(highlightbackground="#00f0ff") 
            self.advance_mission(9)
        elif self.mission_stage == 9 and self.semantics.last_observed == "aegis":
            self.advance_mission(10)
        elif self.mission_stage == 10 and "energy" in self.semantics.symbol_table and int(self.semantics.symbol_table["energy"]["value"]) <= 0:
            self.timeline_state = "stable"
            self.advance_mission(11)

    def advance_mission(self, next_stage):
        # Transitions to next mission stage and resets temporary state
        self.mission_stage = next_stage
        self.semantics.last_observed = None
        self.load_mission()

    def reset_system(self):
        # Clears all symbol tables and resets mission to stage 1
        print(f"\n{Color.YELLOW}[SYSTEM] Wiping memory architecture...{Color.RESET}")
        self.semantics.symbol_table.clear() 
        self.semantics.snapshots.clear()
        self.semantics.entities.clear()
        self.semantics.last_observed = None
        self.semantics.current_offset = 0 
        self.semantics.level_offsets = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0} 
        self.semantics.current_level = 0
        self.update_memory_ui()
        
        if self.mode == "sandbox":
            print(f"{Color.GREEN}System reset complete. Free play resumed.{Color.RESET}\n")
            return
            
        print(f"{Color.CYAN}Timeline manually reset. Reinitalizing Protocol...{Color.RESET}\n")
        self.timeline_state = "fractured"
        self.degradation_level = 95
        self.advance_mission(1)
        self.flash_warnings()

    def update_memory_ui(self):
        # Updates symbol table display with current variables and snapshots
        if not hasattr(self, 'memory_display') or not self.memory_display.winfo_exists(): return
        self.memory_display.configure(state='normal')
        self.memory_display.delete(1.0, tk.END)
        
        self.memory_display.insert(tk.END, f" {'Identifier':<12} | {'Data Type':<9} | {'Level':<5} | {'Offset'}\n", "header")
        self.memory_display.insert(tk.END, "-"*56 + "\n", "dim")
        
        if not self.semantics.symbol_table:
            self.memory_display.insert(tk.END, "\n [ Memory Empty ]\n", "dim")
        else:
            for key, data in self.semantics.symbol_table.items():
                self.memory_display.insert(tk.END, f" {key:<12} | {data['type']:<9} | {data['level']:<5} | {data['offset']}\n")
                
        self.memory_display.insert(tk.END, "\n\n --- ARCHIVED SNAPSHOTS ---\n", "header")
        if not self.semantics.snapshots:
            self.memory_display.insert(tk.END, " [ No snapshots saved ]\n", "dim")
        else:
            for snap_name in self.semantics.snapshots.keys():
                clean_name = snap_name.replace('"', '')
                self.memory_display.insert(tk.END, f"  -> {clean_name}\n")
                
        self.memory_display.tag_config("dim", foreground="#4d6b99")
        self.memory_display.tag_config("header", foreground="#ffe600", font=("Consolas", 11, "bold"))
        self.memory_display.configure(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = ParadoxUI(root)
    root.mainloop()