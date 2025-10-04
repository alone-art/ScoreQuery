import base64
import httpx
from io import BytesIO
import re

from paddleocr import PaddleOCR
from PIL import Image, ImageDraw, ImageEnhance
import numpy

from gsuid_core.sv import SV, get_plugin_available_prefix
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.logger import logger
from gsuid_core.utils.image.convert import convert_img

from ....WutheringWavesUID.WutheringWavesUID.utils.calculate import (
    calc_phantom_entry,
    calc_phantom_score,
    get_calc_map,
    get_max_score,
    get_total_score_bg,
    get_valid_color,
)
from ....WutheringWavesUID.WutheringWavesUID.utils.api.model import (
    AccountBaseInfo,
    OnlineRoleList,
    RoleDetailData,
    WeaponData,
    Props,
)
from ....WutheringWavesUID.WutheringWavesUID.utils.image import (
    GOLD,
    GREY,
    SPECIAL_GOLD,
    WAVES_FREEZING,
    WAVES_MOONLIT,
    WAVES_SHUXING_MAP,
    WEAPON_RESONLEVEL_COLOR,
    add_footer,
    change_color,
    draw_text_with_shadow,
    get_attribute,
    get_attribute_effect,
    get_attribute_prop,
    get_custom_gaussian_blur,
    get_event_avatar,
    get_role_pile,
    get_small_logo,
    get_square_avatar,
    get_square_weapon,
    get_waves_bg,
    get_weapon_type,
)
from ....WutheringWavesUID.WutheringWavesUID.utils.fonts.waves_fonts import (
    waves_font_16,
    waves_font_18,
    waves_font_20,
    waves_font_24,
    waves_font_25,
    waves_font_26,
    waves_font_28,
    waves_font_30,
    waves_font_36,
    waves_font_40,
    waves_font_42,
    waves_font_50,
)
from ....WutheringWavesUID.WutheringWavesUID.utils.name_convert import alias_to_char_name, char_name_to_char_id

async def get_image(ev: Event):
    res = []
    for content in ev.content:
        if (
            content.type == "img"
            and content.data
            and isinstance(content.data, str)
            and content.data.startswith("http")
        ):
            res.append(content.data)
        elif (
            content.type == "image"
            and content.data
            and isinstance(content.data, str)
            and content.data.startswith("http")
        ):
            res.append(content.data)

    if not res and ev.image:
        res.append(ev.image)

    return res

valid_keys = {
    "小生命",
    "生命",
    "小攻击",
    "攻击",
    "小防御",
    "防御",
    "共鸣效率",
    "暴击伤害",
    "暴击",
    "普攻伤害加成",
    "重击伤害加成",
    "共鸣技能伤害加成",
    "共鸣解放伤害加成",
    "气动伤害加成",
    "冷凝伤害加成",
    "导电伤害加成",
    "衍射伤害加成",
    "湮灭伤害加成",
    "热熔伤害加成",
    "治疗效果加成",
}
valid_values = {
    "320", "360", "390", "430", "470", "510", "540", "580",
    "30", "40", "50", "60",
    "70",
    "6.4%", "7.1%", "7.9%", "8.6%", "9.4%", "10.1%", "10.9%", "11.6%",
    "8.1%", "9.0%", "10.0%", "10.9%", "11.8%", "12.8%", "13.8%", "14.7%",
    "6.8%", "7.6%", "8.4%", "9.2%", "10.0%", "10.8%", "11.6%", "12.4%",
    "6.3%", "6.9%", "7.5%", "8.1%", "8.7%", "9.3%", "9.9%", "10.5%",
    "12.6%","13.8%","15.0%","16.2%","17.4%","18.6%","19.8%","21.0%",
}

def extract_vaild_info(info):
    keys = []
    values = []
    for txt in info:
        if len(keys) >= 7 and len(values) >= 7:
            break
        
        if len(keys) < 7:
            if txt in valid_keys:
                keys.append(txt)
            else:
                for k in valid_keys:
                    if k in txt:
                        keys.append(k)
                        break
        if len(values) < 7:
            if len(values) < 2:
                if '%' in txt:
                    values.append(txt)
                else:
                    try:
                        v = int(txt)
                        if v <= 2280 and v >= 30:
                            values.append(txt)
                    except ValueError:
                        pass
            elif txt in valid_values:
                values.append(txt)

    return keys, values



async def get_ocr_text(img):
    result = ocr.predict(input=numpy.array(img))
    return result


async def draw_ph(char_name, props, cost, calc_map):
    _score, _level = calc_phantom_score(
                    char_name, props, cost, calc_map
                )
    _level = _level.upper()
    logger.info(f"{char_name} [声骸分数]: {_score} [声骸评分等级]: {_level}")
    
    img = Image.new("RGBA", (540, 680), (30, 45, 65, 0))
    
    sh_temp_bg_draw = ImageDraw.Draw(img)
    sh_temp_bg_draw.rounded_rectangle(
        [20, 25, 520, 132], radius=12, fill=(25, 35, 55, 10)
    )
    
    rect_width = (len(str(_score)) + len(str(_level)) + 3) * 18 + 20
    ph_score_img = Image.new("RGBA", (rect_width, 36), (255, 255, 255, 0))
    ph_score_img_draw = ImageDraw.Draw(ph_score_img)
    ph_score_img_draw.rounded_rectangle(
        [0, 0, ph_score_img.size[0], ph_score_img.size[1]], radius=8, fill=(186, 55, 42, int(0.8 * 255))
    )
    ph_score_img_draw.text(
        (rect_width / 2, 18), f"{_score}分 {_level}", "white", waves_font_36, "mm"
    )
    img.alpha_composite(ph_score_img, (280, 70))
    
    ph_name_draw = ImageDraw.Draw(img)
    ph_name_draw.text(
        (78, 73), f"{char_name} ", "white", waves_font_36, "lm"
    )
    ph_name_draw.text(
        (78, 105), f"Cost {str(cost)}", "white", waves_font_18, "lm"
    )

    sh_temp = Image.new("RGBA", (404, 402), (25, 35, 55, 10))
    oset = 55
    for index, _prop in enumerate(props):
        _score, final_score = calc_phantom_entry(index, _prop, cost, calc_map)
        logger.info(f"{char_name} [属性]: {_prop.attributeName} {_prop.attributeValue} [评分]: {final_score}")
        
        prop_img = await get_attribute_prop(_prop.attributeName)
        prop_img = prop_img.resize((40, 40))
        sh_temp.alpha_composite(prop_img, (15, 15 + index * oset))
        
        sh_temp_draw = ImageDraw.Draw(sh_temp)
        name_color = "white"
        num_color = "white"
        if index > 1:
            name_color, num_color = get_valid_color(
                _prop.attributeName, _prop.attributeValue, calc_map
            )
            
        sh_temp_draw.text(
            (60, 35 + index * oset),
            f"{_prop.attributeName[:6]}",
            name_color,
            waves_font_24,
            "lm",
        )
        sh_temp_draw.text(
            (318, 35 + index * oset),
            f"{_prop.attributeValue}",
            num_color,
            waves_font_24,
            "rm",
        )
        
        score_color = WAVES_MOONLIT
        if final_score > 0:
            score_color = WAVES_FREEZING
        sh_temp_draw.text(
            (388, 38 + index * oset),
            f"{final_score}分",
            score_color,
            waves_font_18,
            "rm",
        )
    
    sh_temp_bg_draw = ImageDraw.Draw(img)
    sh_temp_bg_draw.rounded_rectangle(
        [20, 146, 520, 580], radius=12, fill=(25, 35, 55, 10)
    )
    img.alpha_composite(sh_temp, (68, 162))
    img = add_footer(img)
    return img


ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False)

from .config import seconfig

sv_phantom_scorer = SV("鸣潮声骸查分")
PREFIX = get_plugin_available_prefix("ScoreQuery")

@sv_phantom_scorer.on_command(('查分'))
async def score_phantom_handler(bot: Bot, ev: Event):
    """
    处理声骸查分请求，调用外部 API 并返回结果。
    """
    upload_images = await get_image(ev)
    if not upload_images:
        await bot.send("请在发送命令的同时附带需要查分的声骸截图哦", at_sender=True)
        return

    cost = 0
    command_str = ev.text.strip().split("查分", 1)[-1].strip()
    # logger.info(f"命令内容: {command_str}")

    for index, v in enumerate(["1c", "3c", "4c"]):
        if v in command_str:
            command_str = command_str.replace(v, "")
            cost = [1,3,4][index]
            break
            
    char_name = alias_to_char_name(command_str)
    logger.info(f"角色名: {char_name}, cost: {cost}")

    char_id = char_name_to_char_id(char_name)
    if not char_id:
        await bot.send(f"[鸣潮] 角色名【{command_str}】无法找到, 可能暂未适配, 请先检查输入是否正确！\n", at_sender=True)
        return
        
    calc_temp = get_calc_map({}, char_name, -1)

    try:
        async with httpx.AsyncClient() as client:
            for image_url in upload_images:
                # 下载图片
                resp = await client.get(image_url)
                resp.raise_for_status()
                image_bytes = resp.content

                props = []
                with Image.open(BytesIO(image_bytes)) as img:
                    if img.mode not in ("RGB"):
                        img = img.convert("RGB")

                    result = await get_ocr_text(img)
                    contexts = result[0].json['res']['rec_texts']
                    logger.info(f"识别内容: {contexts}")
                    keys, values = extract_vaild_info(contexts)
                    logger.info(f"keys: {keys}")
                    logger.info(f"values: {values}")

                    auto_cost = 0
                    if any(cost_str in contexts for cost_str in ["COST 1", "COST1"]):
                        auto_cost = 1
                    elif any(cost_str in contexts for cost_str in ["COST 3", "COST3"]):
                        auto_cost = 3
                    elif any(cost_str in contexts for cost_str in ["COST 4", "COST4"]):
                        auto_cost = 4
                    else:
                        for i, item in enumerate(contexts):
                            if item == "COST" and i + 1 < len(contexts):
                                next_item = str(contexts[i + 1]).strip()
                                if next_item in ["1", "3", "4"]:
                                    auto_cost = int(next_item)
                                break
                    
                    if len(keys) == len(values):
                        for i in range(len(keys)):
                            props.append(Props(attributeName=keys[i].replace("小", ""), attributeValue=values[i]))
                        
                        if auto_cost != 0:
                            ph_img = await draw_ph(char_name, props, auto_cost, calc_temp)
                            ph_img = await convert_img(ph_img)
                            await bot.send(ph_img, at_sender=True)
                        else:
                            if cost == 0:
                                await bot.send(f"未识别cost级别, 请指明, 如查分{command_str}1c\n", at_sender=True)
                            else:
                                ph_img = await draw_ph(char_name, props, cost, calc_temp)
                                ph_img = await convert_img(ph_img)
                                await bot.send(ph_img, at_sender=True)

    except httpx.RequestError as e:
        logger.error(f"下载图片失败: {e}")
        await bot.send("下载图片失败，请稍后再试。", at_sender=True)
        return
    except Exception as e:
        logger.error(f"图片处理失败: {e}")
        await bot.send("图片处理失败，请稍后再试。", at_sender=True)
        return

    # await bot.send(f"处理结束.\n", at_sender=True)



@sv_phantom_scorer.on_command(('ocr','OCR','Ocr'))
async def score_phantom_handler(bot: Bot, ev: Event):
    upload_images = await get_image(ev)
    if not upload_images:
        await bot.send("请在发送命令的同时附带图片", at_sender=True)
        return

    try:
        async with httpx.AsyncClient() as client:
            for image_url in upload_images:
                # 下载图片
                resp = await client.get(image_url)
                resp.raise_for_status()
                image_bytes = resp.content

                with Image.open(BytesIO(image_bytes)) as img:
                    if img.mode not in ("RGB"):
                        img = img.convert("RGB")

                    result = await get_ocr_text(img)
                    for res in result:
                        logger.debug(f"识别内容: {res.json['res']['rec_texts']}")
                        await bot.send(res.json['res']['rec_texts'], at_sender=True)

    except httpx.RequestError as e:
        logger.error(f"下载图片失败: {e}")
        await bot.send("下载图片失败，请稍后再试。", at_sender=True)
        return
    except Exception as e:
        logger.error(f"图片处理失败: {e}")
        await bot.send("图片处理失败，请稍后再试。", at_sender=True)
        return
