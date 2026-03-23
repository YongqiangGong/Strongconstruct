# Copyright (c) Opendatalab. All rights reserved.
import copy
import json
import os
from pathlib import Path

from loguru import logger

from mineru.cli.common import convert_pdf_bytes_to_bytes_by_pypdfium2, prepare_env, read_fn
from mineru.data.data_reader_writer import FileBasedDataWriter
from mineru.utils.draw_bbox import draw_layout_bbox, draw_span_bbox
from mineru.utils.enum_class import MakeMode
from mineru.backend.vlm.vlm_analyze import doc_analyze as vlm_doc_analyze
from mineru.backend.pipeline.pipeline_analyze import doc_analyze as pipeline_doc_analyze
from mineru.backend.pipeline.pipeline_middle_json_mkcontent import union_make as pipeline_union_make
from mineru.backend.pipeline.model_json_to_middle_json import result_to_middle_json as pipeline_result_to_middle_json
from mineru.backend.vlm.vlm_middle_json_mkcontent import union_make as vlm_union_make
from mineru.utils.guess_suffix_or_lang import guess_suffix_by_path


def do_parse(
    output_dir,  # Output directory for storing parsing results
    pdf_file_names: list[str],  # List of PDF file names to be parsed
    pdf_bytes_list: list[bytes],  # List of PDF bytes to be parsed
    p_lang_list: list[str],  # List of languages for each PDF, default is 'ch' (Chinese)
    backend="pipeline",  # The backend for parsing PDF, default is 'pipeline'
    parse_method="auto",  # The method for parsing PDF, default is 'auto'
    formula_enable=True,  # Enable formula parsing
    table_enable=True,  # Enable table parsing
    server_url=None,  # Server URL for vlm-http-client backend
    f_draw_layout_bbox=True,  # Whether to draw layout bounding boxes
    f_draw_span_bbox=True,  # Whether to draw span bounding boxes
    f_dump_md=True,  # Whether to dump markdown files
    f_dump_middle_json=True,  # Whether to dump middle JSON files
    f_dump_model_output=True,  # Whether to dump model output files
    f_dump_orig_pdf=True,  # Whether to dump original PDF files
    f_dump_content_list=True,  # Whether to dump content list files
    f_make_md_mode=MakeMode.MM_MD,  # The mode for making markdown content, default is MM_MD
    start_page_id=0,  # Start page ID for parsing, default is 0
    end_page_id=None,  # End page ID for parsing, default is None (parse all pages until the end of the document)
):

    if backend == "pipeline":
        for idx, pdf_bytes in enumerate(pdf_bytes_list):
            new_pdf_bytes = convert_pdf_bytes_to_bytes_by_pypdfium2(pdf_bytes, start_page_id, end_page_id)
            pdf_bytes_list[idx] = new_pdf_bytes

        infer_results, all_image_lists, all_pdf_docs, lang_list, ocr_enabled_list = pipeline_doc_analyze(pdf_bytes_list, p_lang_list, parse_method=parse_method, formula_enable=formula_enable,table_enable=table_enable)

        for idx, model_list in enumerate(infer_results):
            model_json = copy.deepcopy(model_list)
            pdf_file_name = pdf_file_names[idx]
            local_image_dir, local_md_dir = prepare_env(output_dir, pdf_file_name, parse_method)
            image_writer, md_writer = FileBasedDataWriter(local_image_dir), FileBasedDataWriter(local_md_dir)

            images_list = all_image_lists[idx]
            pdf_doc = all_pdf_docs[idx]
            _lang = lang_list[idx]
            _ocr_enable = ocr_enabled_list[idx]
            middle_json = pipeline_result_to_middle_json(model_list, images_list, pdf_doc, image_writer, _lang, _ocr_enable, formula_enable)

            pdf_info = middle_json["pdf_info"]

            pdf_bytes = pdf_bytes_list[idx]
            _process_output(
                pdf_info, pdf_bytes, pdf_file_name, local_md_dir, local_image_dir,
                md_writer, f_draw_layout_bbox, f_draw_span_bbox, f_dump_orig_pdf,
                f_dump_md, f_dump_content_list, f_dump_middle_json, f_dump_model_output,
                f_make_md_mode, middle_json, model_json, is_pipeline=True
            )
    else:
        if backend.startswith("vlm-"):
            backend = backend[4:]

        f_draw_span_bbox = False
        parse_method = "vlm"
        for idx, pdf_bytes in enumerate(pdf_bytes_list):
            pdf_file_name = pdf_file_names[idx]
            pdf_bytes = convert_pdf_bytes_to_bytes_by_pypdfium2(pdf_bytes, start_page_id, end_page_id)
            local_image_dir, local_md_dir = prepare_env(output_dir, pdf_file_name, parse_method)
            image_writer, md_writer = FileBasedDataWriter(local_image_dir), FileBasedDataWriter(local_md_dir)
            middle_json, infer_result = vlm_doc_analyze(pdf_bytes, image_writer=image_writer, backend=backend, server_url=server_url)

            pdf_info = middle_json["pdf_info"]

            _process_output(
                pdf_info, pdf_bytes, pdf_file_name, local_md_dir, local_image_dir,
                md_writer, f_draw_layout_bbox, f_draw_span_bbox, f_dump_orig_pdf,
                f_dump_md, f_dump_content_list, f_dump_middle_json, f_dump_model_output,
                f_make_md_mode, middle_json, infer_result, is_pipeline=False
            )


def _process_output(
        pdf_info,
        pdf_bytes,
        pdf_file_name,
        local_md_dir,
        local_image_dir,
        md_writer,
        f_draw_layout_bbox,
        f_draw_span_bbox,
        f_dump_orig_pdf,
        f_dump_md,
        f_dump_content_list,
        f_dump_middle_json,
        f_dump_model_output,
        f_make_md_mode,
        middle_json,
        model_output=None,
        is_pipeline=True
):
    """处理输出文件"""
    if f_draw_layout_bbox:
        draw_layout_bbox(pdf_info, pdf_bytes, local_md_dir, f"{pdf_file_name}_layout.pdf")

    if f_draw_span_bbox:
        draw_span_bbox(pdf_info, pdf_bytes, local_md_dir, f"{pdf_file_name}_span.pdf")

    if f_dump_orig_pdf:
        md_writer.write(
            f"{pdf_file_name}_origin.pdf",
            pdf_bytes,
        )

    image_dir = str(os.path.basename(local_image_dir))

    if f_dump_md:
        make_func = pipeline_union_make if is_pipeline else vlm_union_make
        md_content_str = make_func(pdf_info, f_make_md_mode, image_dir)
        md_writer.write_string(
            f"{pdf_file_name}.md",
            md_content_str,
        )

    if f_dump_content_list:
        make_func = pipeline_union_make if is_pipeline else vlm_union_make
        content_list = make_func(pdf_info, MakeMode.CONTENT_LIST, image_dir)
        md_writer.write_string(
            f"{pdf_file_name}_content_list.json",
            json.dumps(content_list, ensure_ascii=False, indent=4),
        )

    if f_dump_middle_json:
        md_writer.write_string(
            f"{pdf_file_name}_middle.json",
            json.dumps(middle_json, ensure_ascii=False, indent=4),
        )

    if f_dump_model_output:
        md_writer.write_string(
            f"{pdf_file_name}_model.json",
            json.dumps(model_output, ensure_ascii=False, indent=4),
        )

    logger.info(f"local output dir is {local_md_dir}")


def parse_doc(
        path_list: list[Path],
        output_dir,
        lang="ch",
        backend="pipeline",
        method="auto",
        server_url=None,
        start_page_id=0,
        end_page_id=None
):
    """
        Parameter description:
        path_list: List of document paths to be parsed, can be PDF or image files.
        output_dir: Output directory for storing parsing results.
        lang: Language option, default is 'ch', optional values include['ch', 'ch_server', 'ch_lite', 'en', 'korean', 'japan', 'chinese_cht', 'ta', 'te', 'ka']。
            Input the languages in the pdf (if known) to improve OCR accuracy.  Optional.
            Adapted only for the case where the backend is set to "pipeline"
        backend: the backend for parsing pdf:
            pipeline: More general.
            vlm-transformers: More general.
            vlm-vllm-engine: Faster(engine).
            vlm-http-client: Faster(client).
            without method specified, pipeline will be used by default.
        method: the method for parsing pdf:
            auto: Automatically determine the method based on the file type.
            txt: Use text extraction method.
            ocr: Use OCR method for image-based PDFs.
            Without method specified, 'auto' will be used by default.
            Adapted only for the case where the backend is set to "pipeline".
        server_url: When the backend is `http-client`, you need to specify the server_url, for example:`http://127.0.0.1:30000`
        start_page_id: Start page ID for parsing, default is 0
        end_page_id: End page ID for parsing, default is None (parse all pages until the end of the document)
    """
    # 存储解析失败的文件信息，用于后续导出清单
    error_files = []
    total_files = len(path_list)
    logger.info(f"开始解析任务，共发现 {total_files} 个待处理文件")

    try:
        # 遍历每个文件，逐个解析（单独捕获每个文件的异常）
        for idx, path in enumerate(path_list, start=1):
            # 跳过目录或隐藏文件（避免无效文件触发错误）
            if path.is_dir() or path.name.startswith("."):
                logger.warning(f"[{idx}/{total_files}] 跳过非文件/隐藏文件：{path}")
                continue

            file_name = str(Path(path).stem)
            try:
                logger.info(f"[{idx}/{total_files}] 开始解析文件：{file_name}（路径：{path}）")
                # 读取单个文件的字节数据
                pdf_bytes = read_fn(path)
                # 构造单个文件的参数列表（适配原有 do_parse 函数接口）
                file_name_list = [file_name]
                pdf_bytes_list = [pdf_bytes]
                lang_list = [lang]

                # 调用 do_parse 解析当前单个文件
                do_parse(
                    output_dir=output_dir,
                    pdf_file_names=file_name_list,
                    pdf_bytes_list=pdf_bytes_list,
                    p_lang_list=lang_list,
                    backend=backend,
                    parse_method=method,
                    server_url=server_url,
                    start_page_id=start_page_id,
                    end_page_id=end_page_id
                )
                logger.success(f"[{idx}/{total_files}] 文件解析成功：{file_name}")

            # 捕获单个文件的解析错误，记录后继续下一个
            except Exception as e:
                error_info = {
                    "文件序号": idx,
                    "文件名": file_name,
                    "文件路径": str(path),
                    "错误信息": str(e),
                    "错误类型": type(e).__name__
                }
                error_files.append(error_info)
                logger.error(f"[{idx}/{total_files}] 解析失败！文件名：{file_name}，错误：{str(e)}")
                continue

        # 任务结束后，导出失败文件清单（如果有失败文件）
        if error_files:
            # 确保输出目录存在
            os.makedirs(output_dir, exist_ok=True)
            error_log_path = os.path.join(output_dir, "解析失败文件清单.json")
            with open(error_log_path, "w", encoding="utf-8") as f:
                json.dump(error_files, f, ensure_ascii=False, indent=4)
            logger.warning(f"解析任务完成！共 {len(error_files)}/{total_files} 个文件失败，清单已保存至：{error_log_path}")
        else:
            logger.success(f"解析任务完成！所有 {total_files} 个文件均解析成功")

    # 捕获整体流程的致命错误（如输出目录创建失败、参数异常等）
    except Exception as e:
        logger.exception(f"解析任务整体异常（非单个文件错误）：{str(e)}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description="MiniPDF 解析工具：支持指定输入目录和输出目录"
    )
    parser.add_argument("input_dir", type=str, help="输入文档目录（支持 PDF 和常见图像格式）")
    parser.add_argument("output_dir", type=str, help="输出结果目录")
    parser.add_argument("--backend", type=str, default="pipeline",
                        choices=["pipeline", "vlm-transformers", "vlm-mlx-engine", "vlm-vllm-engine", "vlm-http-client"],
                        help="解析后端，默认为 pipeline")
    parser.add_argument("--server_url", type=str, default=None,
                        help="当 backend 为 vlm-http-client 时，需指定服务地址，如 http://127.0.0.1:30000")
    parser.add_argument("--lang", type=str, default="ch",
                        choices=["ch", "ch_server", "ch_lite", "en", "korean", "japan", "chinese_cht", "ta", "te", "ka"],
                        help="文档语言（仅 pipeline 后端有效）")
    parser.add_argument("--method", type=str, default="auto",
                        choices=["auto", "txt", "ocr"],
                        help="解析方法（仅 pipeline 后端有效）")
    parser.add_argument("--start_page", type=int, default=0, help="起始页码（从0开始）")
    parser.add_argument("--end_page", type=int, default=None, help="结束页码（不包含），默认解析全部")

    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = args.output_dir  # 保持为字符串，与原函数签名一致

    if not input_dir.exists() or not input_dir.is_dir():
        logger.error(f"输入目录不存在或不是文件夹: {input_dir}")
        exit(1)

    pdf_suffixes = ["pdf"]
    image_suffixes = ["png", "jpeg", "jp2", "webp", "gif", "bmp", "jpg"]

    doc_path_list = [
        p for p in input_dir.glob('*')
        if p.is_file() and not p.name.startswith('.') and guess_suffix_by_path(p) in (pdf_suffixes + image_suffixes)
    ]

    if not doc_path_list:
        logger.warning(f"在 {input_dir} 中未找到支持的文档文件（PDF 或图像）")
        exit(0)

    """如果您由于网络问题无法下载模型，可以设置环境变量MINERU_MODEL_SOURCE为modelscope使用免代理仓库下载模型"""
    os.environ.setdefault('MINERU_MODEL_SOURCE', 'modelscope')

    parse_doc(
        path_list=doc_path_list,
        output_dir=output_dir,
        lang=args.lang,
        backend=args.backend,
        method=args.method,
        server_url=args.server_url,
        start_page_id=args.start_page,
        end_page_id=args.end_page
    )

    """To enable VLM mode, change the backend to 'vlm-xxx'"""
    # parse_doc(doc_path_list, output_dir, backend="vlm-transformers")  # more general.
    # parse_doc(doc_path_list, output_dir, backend="vlm-mlx-engine")  # faster than transformers in macOS 13.5+.
    # parse_doc(doc_path_list, output_dir, backend="vlm-vllm-engine")  # faster(engine).
    # parse_doc(doc_path_list, output_dir, backend="vlm-http-client", server_url="http://127.0.0.1:30000")  # faster(client).