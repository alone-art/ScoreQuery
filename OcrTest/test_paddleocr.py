from paddleocr import PaddleOCR
from PIL import Image

ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False)

# 对示例图像执行 OCR 推理 
result = ocr.predict(
    input="example1.png")
    
    
# print(f"keys: { result[0].key }")
# print(f"{ result[0].rec_texts }")
# 可视化结果并保存 json 结果
for res in result:
    print(f"{ dir(res) }\n")
    print(f"{ dir(res.json) }\n")
    print(f"{ type(res.json) }\n")
    print(f"{ res.json['res']['rec_texts'] }")
    
    # res.print()
    # res.save_to_img("output")
    # res.save_to_json("output")

    
# result = ocr.predict(
#     input="example2.png")
    
# # 可视化结果并保存 json 结果
# for res in result:
#     res.print()
#     # res.save_to_img("output")
#     # res.save_to_json("output")