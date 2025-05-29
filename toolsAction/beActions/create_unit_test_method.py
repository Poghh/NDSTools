import json


def create_unit_test_method(
    screen_code: str, service_name: str, endpoint: str, json_raw: str
) -> str:
    # Tên method test
    method_name = (
        "test" + screen_code + "".join(x.capitalize() for x in service_name.split("_"))
    )

    # Tên log message
    log_label = (
        f"{screen_code} {''.join(x.capitalize() for x in service_name.split('_'))}"
    )

    # Endpoint URL
    endpoint_url = f"/cmn/{endpoint}"

    # Comment đầu method
    method_comment = f"{screen_code}_課題分析"

    # Chuyển JSON thành chuỗi nối đúng format
    try:
        json_obj = json.loads(json_raw)
        pretty_json = json.dumps(json_obj, indent=4, ensure_ascii=False)
    except Exception as e:
        return f"// JSON không hợp lệ: {str(e)}"

    java_json = '        String parameterMapJson = "'  # dòng đầu
    lines = pretty_json.splitlines()

    # Nối từng dòng với escape dấu "
    for idx, line in enumerate(lines):
        escaped_line = line.replace("\\", "\\\\").replace('"', '\\"')  # escape " và \
        if idx == 0:
            java_json += escaped_line + '" +\n'
        elif idx == len(lines) - 1:
            java_json += '                                "' + escaped_line + '";'
        else:
            java_json += '                                "' + escaped_line + '" +\n'

    # Java unit test method string
    java_code = f"""\
/**
 * {method_comment}
 */
@Test
public void {method_name}() throws Exception {{
        // Request Body JSON設定：内容は、フロントエンド側のMOCK APIの実行結果（Chrome consoleログ）から取得する
{java_json}

        MockHttpServletRequestBuilder postRequest = MockMvcRequestBuilders.post("{endpoint_url}")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(parameterMapJson);

        final String contentAsString = this.mockMvc.perform(postRequest.with(request -> {{
                // リクエストヘッダ－：認証トークン（固定）
                request.addHeader("X-AUTH-TOKEN", "token1");
                // リクエストヘッダ－：契約者ID（固定）
                request.addHeader("X-CLIENT-SSL-CN", "SCM00CB");
                // リクエストヘッダ－：XMLHttpRequest（固定）
                request.addHeader("X-Requested-With", "XMLHttpRequest");
                return request;
        }}))
                        // レスポンス結果をログ出力する。
                        .andDo(MockMvcResultHandlers.print())
                        .andExpect(MockMvcResultMatchers.status().isOk())
                        .andReturn()
                        .getResponse()
                        .getContentAsString();

        // HTTPレスポンス（MOCK）の実行結果をログに出力する
        LOG.info("{log_label} Result: {{}}", contentAsString);
}}"""
    return java_code
