import json
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk


class UnitTestDialog(tk.Toplevel):
    def __init__(self, parent, screen_code=None):
        super().__init__(parent)
        self.title("Sinh Unit Test")
        self.geometry("800x800")
        self.lift()
        self.screen_code = screen_code
        self.build_ui()

    def build_ui(self):
        tk.Label(self, text="Mã màn hình (GUIコード):").pack(pady=(10, 0))
        self.screen_code_entry = tk.Entry(self, width=40)
        self.screen_code_entry.insert(0, self.screen_code or "")
        self.screen_code_entry.pack()

        tk.Label(self, text="Tên service:").pack(pady=(10, 0))
        self.service_name_entry = tk.Entry(self, width=40)
        self.service_name_entry.pack()

        tk.Label(self, text="Loại xử lý (select/update):").pack(pady=(10, 0))
        self.endpoint_var = tk.StringVar(value="select")
        endpoint_menu = ttk.Combobox(
            self,
            textvariable=self.endpoint_var,
            values=["select", "update"],
            state="readonly",
        )
        endpoint_menu.pack()

        # JSON Input Area
        frame_json_header = tk.Frame(self)
        frame_json_header.pack(fill=tk.X, padx=40, pady=(20, 0))
        tk.Label(frame_json_header, text="Input JSON:").pack(side=tk.LEFT)

        self.json_text = scrolledtext.ScrolledText(self, height=15)
        self.json_text.pack(padx=40, fill=tk.BOTH, expand=True)

        tk.Button(
            frame_json_header,
            text="Validate & Beautify JSON",
            command=lambda: beautify_json(self.json_text),
        ).pack(side=tk.RIGHT)

        tk.Button(self, text="Generate Unit Test Method", command=self.on_generate).pack(pady=5)

        frame_output_text = tk.Frame(self)
        frame_output_text.pack(fill=tk.BOTH, expand=True, padx=40, pady=(10, 20))

        self.output_text = scrolledtext.ScrolledText(frame_output_text, height=15)
        self.output_text.pack(fill=tk.BOTH, expand=True)

    def on_generate(self):
        screen_code = self.screen_code_entry.get().strip()
        service_name = self.service_name_entry.get().strip()
        endpoint = self.endpoint_var.get()
        json_raw = self.json_text.get("1.0", tk.END)

        if not screen_code or not service_name or not json_raw.strip():
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đủ thông tin cần thiết.")
            return

        java_code = create_unit_test_method(screen_code, service_name, endpoint, json_raw)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, java_code)


def beautify_json(json_text_widget):
    try:
        raw = json_text_widget.get("1.0", tk.END).strip()
        parsed = json.loads(raw)
        pretty = json.dumps(parsed, indent=4, ensure_ascii=False)
        json_text_widget.delete("1.0", tk.END)
        json_text_widget.insert(tk.END, pretty)
    except Exception as e:
        messagebox.showerror("Lỗi", f"JSON không hợp lệ:\n{str(e)}")


def extract_gui(screen_code: str):
    if "_" in screen_code:
        return screen_code.split("_")[0]
    else:
        return screen_code.strip()


def create_unit_test_method(screen_code, service_name, endpoint, json_raw):
    method_name = "test" + screen_code + "".join(x.capitalize() for x in service_name.split("_"))
    log_label = f"{screen_code} {''.join(x.capitalize() for x in service_name.split('_'))}"
    method_comment = screen_code
    method_name = "test" + screen_code + "".join(x.capitalize() for x in service_name.split("_"))
    log_label = f"{screen_code} {''.join(x.capitalize() for x in service_name.split('_'))}"
    endpoint_url = f"/cmn/{endpoint}"
    class_name = extract_gui(screen_code) + "Tests"

    try:
        json_obj = json.loads(json_raw)
        pretty_json = json.dumps(json_obj, indent=4, ensure_ascii=False)
    except Exception as e:
        return f"// JSON không hợp lệ: {str(e)}"

    lines = pretty_json.splitlines()
    java_json = '        String parameterMapJson = "' + lines[0].replace('"', '\\"') + '" +\n'
    for line in lines[1:-1]:
        java_json += '                                "' + line.replace('"', '\\"') + '" +\n'
    java_json += '                                "' + lines[-1].replace('"', '\\"') + '";'

    return f"""@RunWith(SpringRunner.class)
@SpringBootTest
public class {class_name} {{

        /**
         * {method_comment}
         */
        @Autowired
        private CareBaseApiController careBaseApiController;
        
        /** ロガー. */
        private static final Logger LOG = LoggerFactory.getLogger(MethodHandles.lookup().lookupClass());

        @Autowired
        private SwitchingDataSourceFilter switchingDataSourceFilter;

        private MockMvc mockMvc;

        @Before
        public void before() {{
                this.mockMvc = MockMvcBuilders.standaloneSetup(this.careBaseApiController)
                                .addFilters(this.switchingDataSourceFilter)
                                .build();
        }}

        /**\n         * {method_comment}\n         */
        @Test
        public void {method_name}() throws Exception {{
                // Request Body JSON設定：内容は、フロントエンド側のMOCK APIの実行結果（Chrome consoleログ）から取得する
{java_json}

                MockHttpServletRequestBuilder postRequest = MockMvcRequestBuilders.post("{endpoint_url}")
                                .contentType(MediaType.APPLICATION_JSON)
                                .content(parameterMapJson);

                final String contentAsString = this.mockMvc.perform(postRequest.with(request -> {{
                        request.addHeader("X-AUTH-TOKEN", "token1");
                        request.addHeader("X-CLIENT-SSL-CN", "SCM00CB");
                        request.addHeader("X-Requested-With", "XMLHttpRequest");
                        return request;
                }}))
                                .andDo(MockMvcResultHandlers.print())
                                .andExpect(MockMvcResultMatchers.status().isOk())
                                .andReturn()
                                .getResponse()
                                .getContentAsString();

                LOG.info("{log_label} Result: {{}}", contentAsString);
        }}
}}"""
