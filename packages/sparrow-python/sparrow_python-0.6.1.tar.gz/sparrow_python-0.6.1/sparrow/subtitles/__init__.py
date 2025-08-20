import pysubs2
from subsai import Tools, SubsAI
from pathlib import Path


# transcribe
def transcribe(filename,
               model_name='m-bain/whisperX',
               model_config={'model_type': 'base', 'device': 'cpu'},
               ):
    subs_ai = SubsAI()
    model = subs_ai.create_model(
        model_name=model_name,
        model_config=model_config,
    )
    subs1 = subs_ai.transcribe(filename, model)
    origin_srt = f"{Path(filename).stem}.srt"
    subs1.save(origin_srt)
    print(f"origin file saved to {origin_srt}")
    return origin_srt


def translate(subtitles_file,
              source_language='English',

              target_language='Chinese',
              # translation_model='facebook/m2m100_418M',
              translation_model='mbart50',

              # target_language='Chinese (Simplified)',
              # translation_model='facebook/nllb-200-distilled-600M', # 效果不咋地

              ):
    subs = pysubs2.load(subtitles_file)
    # Tools.available_translation_languages(translation_model)
    format = 'srt'
    translated_file = f"{Path(subtitles_file).stem}_{target_language}.{format}"

    translated_subs = Tools.translate(subs,
                                      source_language=source_language,
                                      target_language=target_language,
                                      model=translation_model)

    translated_subs.save(translated_file)
    print(f"translated file saved to {translated_file}")
    return translated_file


def merge_subs(srt_en: str, srt_zh: str):

    subs_en = pysubs2.load(srt_en)
    subs_zh = pysubs2.load(srt_zh)
    subs_bi_lang = pysubs2.SSAFile()
    for sub_zh, sub_en in zip(subs_zh, subs_en):
        sub_zh: pysubs2.SSAEvent
        sub = sub_zh.copy()
        sub.text += f"\n{sub_en.text}\n"
        subs_bi_lang.append(sub)

    srt_en = Path(srt_en)
    target_srt = f"{srt_en.stem}-merged.srt"
    print(f"merged file saved to {target_srt}")
    subs_bi_lang.save(target_srt)


def merge_subs_with_video(file: str, srt_en: str, srt_zh: str):
    subs_en = pysubs2.load(srt_en)
    subs_zh = pysubs2.load(srt_zh)
    Tools.merge_subs_with_video({'English': subs_en, "Chinese": subs_zh}, file)

if __name__ == "__main__":
    file = 'test.wav'
    # origin_srt = transcribe(file)
    # translated_srt = translate(origin_srt)
    origin_srt = 'test.srt'
    translated_srt = 'test.srt-English-Chinese.srt'
    merge_subs(origin_srt, translated_srt)
