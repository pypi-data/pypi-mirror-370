# Vision Models

Reading documents like Word, PDF, or PowerPoint can sometimes be complicated if they contain images. To avoid this problem, **you can use visual language models (VLMs), which are capable of recognizing images and extracting descriptions from them**. In this prospectus, a model module has been developed, the implementation of which is based on the **BaseModel** class. It is presented below.

## Which model should I use?

The choice of model depends on your cloud provider, available API keys, and desired level of integration.
All models inherit from **BaseModel** and provide the same interface for extracting text and descriptions from images.

| Model                    | When to use                                                      | Requirements                                                                 | Features                                                                                 |
| ------------------------ | ---------------------------------------------------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| [**Open AI Vision Model**](#openaivisionmodel)      | Use if you have an OpenAI API key and want to use OpenAI cloud   | **OPENAI_API_KEY**  (optional: **OPENAI_MODEL**, defaults to **"gpt-4.1"**)           | Simple setup; standard OpenAI chat API.                                                  |
| [**Azure OpenAI Vision Model**](#azureopenaivisionmodel) | Use if your organization uses Azure OpenAI Services              | **AZURE_OPENAI_API_KEY**, **AZURE_OPENAI_ENDPOINT**, **AZURE_OPENAI_DEPLOYMENT**   | Integrates with Azure; enterprise controls; uses Azure’s Responses/Chat API.             |
| [**Grok Vision Model**](#grokvisionmodel)        | Use if you have access to xAI’s Grok multimodal model            | **XAI_API_KEY** (optional: **XAI_MODEL**, defaults to **"grok-4"**)                | Supports image data-URIs; **optional** **image_url.detail** (**"low"**, **"auto"**, **"high"**). |
| [**`BaseModel`**](#basemodel)              | Abstract base, not used directly                                 | –                                                                            | Use as a template for building your own adapters.                                        |

## Models

### BaseModel

::: src.splitter_mr.model.base_model
    handler: python
    options:
      members_order: source

### OpenAIVisionModel

![OpenAIVisionModel logo](../assets/openai_vision_model_button.svg#gh-light-mode-only)
![OpenAIVisionModel logo](../assets/openai_vision_model_button_white.svg#gh-dark-mode-only)

::: src.splitter_mr.model.models.openai_model
    handler: python
    options:
      members_order: source

### AzureOpenAIVisionModel

![OpenAIVisionModel logo](../assets/azure_openai_vision_model_button.svg#gh-light-mode-only)
![OpenAIVisionModel logo](../assets/azure_openai_vision_model_button_white.svg#gh-dark-mode-only)

::: src.splitter_mr.model.models.azure_openai_model
    handler: python
    options:
      members_order: source

### GrokVisionModel

![GrokVisionModel logo](../assets/grok_vision_model_button.svg#gh-light-mode-only)
![GrokVisionModel logo](../assets/grok_vision_model_button_white.svg#gh-dark-mode-only)

::: src.splitter_mr.model.models.grok_model
    handler: python
    options:
      members_order: source