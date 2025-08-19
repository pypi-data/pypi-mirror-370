from syrius.commands import ArrayFilterByCommand, ArrayKeyValueCommand, ArrayLengthCommand, \
    ArrayOfKeyValueToArrayCommand, ArrayReduceByKeyCommand, ArraysMergeByKeyCommand, CurrencyFormatterCommand, \
    FileTextExtractCommand, FileUploadCommand, GrtCommand, IfCommand, OpenAICompletionCommand, \
    PdfHighlighterCommand, SectionSplitterCommand, SectionRemoverCommand, SentencesSplitterCommand, TemplateCommand, \
    UnstructuredCommand, LoopInputCommand, PdfToMarkdownCommand, ArraysKeyValueMergeCommand, ArraysMergeCommand, \
    AzureCompletionCommand, TokenCounterCommand, AnthropicCompletionCommand, JoinAudioCommand, \
    OpenAITextToSpeechCommand, AWSSESSendEmailCommand, AWSS3SaveObjectCommand, AWSPollyGenerateCommand, \
    AzureTextToSpeechCommand, GoogleTextToSpeechCommand, ArraysGetKeyCommand, RandomStringCommand, GetFileNameCommand
from syrius.loops.ForCommand import ForCommand

commands_union = (ArrayKeyValueCommand | ArrayLengthCommand | ArraysMergeByKeyCommand | CurrencyFormatterCommand
                  | FileTextExtractCommand | FileUploadCommand | GrtCommand | IfCommand | LoopInputCommand
                  | OpenAICompletionCommand | SectionRemoverCommand | SectionSplitterCommand | SentencesSplitterCommand
                  | TemplateCommand | UnstructuredCommand | ArrayOfKeyValueToArrayCommand | PdfHighlighterCommand
                  | ArrayFilterByCommand | ArrayReduceByKeyCommand | PdfToMarkdownCommand | ArraysKeyValueMergeCommand
                  | ArraysMergeCommand | AzureCompletionCommand | TokenCounterCommand | AnthropicCompletionCommand
                  | JoinAudioCommand | OpenAITextToSpeechCommand | AWSSESSendEmailCommand | AWSS3SaveObjectCommand
                  | AWSPollyGenerateCommand | AzureTextToSpeechCommand | GoogleTextToSpeechCommand | ArraysGetKeyCommand
                  | RandomStringCommand | GetFileNameCommand | ForCommand)
