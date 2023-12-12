# google-translate

* domain(s): pairs, pretrain, translation
* accepts: ldc.supervised.pairs.PairData, ldc.pretrain.PretrainData, ldc.translation.TranslationData
* generates: ldc.supervised.pairs.PairData, ldc.pretrain.PretrainData, ldc.translation.TranslationData

Translates text using Google's Translate API. The 'project_id' refers to your project ID in the Google Cloud console (http://console.cloud.google.com/). The Google Translate API must be enabled. Requires local dev credentials: https://cloud.google.com/docs/authentication/provide-credentials-adc#local-dev

```
usage: google-translate [-h] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                        [-N LOGGER_NAME] [-p PROJECT_ID] [-s SOURCE_LANG]
                        [-t TARGET_LANG] [--split_lines]
                        [-L [{any,instruction,input,output,content} [{any,instruction,input,output,content} ...]]]

Translates text using Google's Translate API. The 'project_id' refers to your
project ID in the Google Cloud console (http://console.cloud.google.com/). The
Google Translate API must be enabled. Requires local dev credentials:
https://cloud.google.com/docs/authentication/provide-credentials-adc#local-dev

optional arguments:
  -h, --help            show this help message and exit
  -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        The logging level to use. (default: WARN)
  -N LOGGER_NAME, --logger_name LOGGER_NAME
                        The custom name to use for the logger, uses the plugin
                        name by default (default: None)
  -p PROJECT_ID, --project_id PROJECT_ID
                        The name/ID of the Google Cloud project to use.
                        (default: None)
  -s SOURCE_LANG, --source_lang SOURCE_LANG
                        The language the incoming text is in. (default: None)
  -t TARGET_LANG, --target_lang TARGET_LANG
                        The language to translate the text into. (default:
                        None)
  --split_lines         Whether to split the text on new lines rather than
                        presenting it as a single item to translate. (default:
                        False)
  -L [{any,instruction,input,output,content} [{any,instruction,input,output,content} ...]], --location [{any,instruction,input,output,content} [{any,instruction,input,output,content} ...]]
                        Which data use for counting tokens; pairs:
                        any,instruction,input,output, pretrain: any,content,
                        translation: any,content (default: any)
```
