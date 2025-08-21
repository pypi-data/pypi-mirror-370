# Tikos Reasoning Platform

Tikos Reasoning Platform harnesses the power of empirically established 2nd-generation AI and statistical toolsets to offer its users advanced 3rd-generation AI capabilities.

Copyright 2024 (C) Tikos Technologies Limited

## How to access the platform

To get Alpha API keys, please register your request via https://tikos.tech/

## Licence

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

## Release Notes

1. **v 0.0.7**

   i. Added `GetGraphStructure`: Automatically extract graph Vertices and Edges that can be further refined by the user

   ii. Added `GenerateGraph`: Provide Tikos Reasoning Platform the refined graph Vertices and Edges to build the standard knowledge graph

   iii. Added `GetGraph`: Get the whole graph for an extraction request

   iv. Added `GetGraphRelationships`: Get relationships between two Vertexes

<br>

2. **v 0.0.8**

   i. Added `GetGraphRetrieval`: Retrieve query response along with the Graph relationships for the requested retrieve query

<br>

3. **v 0.0.9**

   i. Added `GetGraphRetrievalWithDS`: Retrieve query response along with the Graph relationships for the requested retrieve query with Graph Node data sets as JSON

<br>

4. **v 0.1.0**

   i. Added licence conditions

<br>

5. **v 0.1.1**

   i. Added `ProcessExtractFile`: Be able to extract data from a specific file and support JSON based extraction using jq based schemas

   ii. Modified `ProcessExtract`: Support JSON based extraction using jq based schemas

<br>

6. **v0.1.1**

   i. Added `BuildSC`: Generate the SequentialCollection knowledge structure for the associated graph Vertices from structured data sets

   ii. Added `GetSimilarCase`: Providing a Problem Space (PS) case, the Sequential collection will contact a basic binary (BIN, default) search or advanced binary (BINADV) search and return the most similar existing case. This does not perform any case adaptation

<br>

7. **v0.1.4**

   i. Added `GetGraphStructurePerDoc`: Accept a file names and generate NER JSON of the (submitted) file

   ii. Added `GenerateGraphPerDoc`: Accept a NER JSON object and create a graph of the (submitted) file

   iii. Added `GenerateAutoGraph`: Accept a list of file names, that will be used to generate the NER generation automatically and create a full graph

<br>

8. **v0.1.6**

   i. Amended `GetGraphRetrieval`: Accept optional file reference and base model reference

   ii. Amended `GetGraphRetrievalWithDS`: Accept optional file reference and base model reference

<br>

9. **v0.1.7**

   i. Added `GetCustomerGraphRetrievalWithDS`: Retrieve customer specific query with the Graph relationships for the requested retrieve query with Graph Node data sets as JSON

<br>

10. **v0.1.8**
    - Amended `GenerateGraph`, `GenerateGraphPerDoc` & `GenerateAutoGraph`: Accept graph generation Payload Configuration with the `JSON` format:
      ```json
      {
        "overrideNER": "<True/False>",
        "filter": "<GRAPH CASE_TYPE ATTRIBUTE GENERATION CONFIG TEXT>"
      }
      ```

<br>

11. **v0.1.9**

    i. Amended `GetGraphStructure`, `GetGraphStructurePerDoc`, `GenerateGraph`, `GenerateGraphPerDoc` & `GenerateAutoGraph`: Accept the model-id configuration

<br>

12. **v0.2.0**

    i. Added `GetReasoning`: Generate Similarity Reasoning of a Solution for a given Sequential Collection Case

<br>

13. **v0.2.1**

    i. Added `tikos.TikosClient`, A generic client connector that orchestrates commonly used base functions. It has been developed to facilitate easy integration with other applications and supports multithreading.

    ii. Added `addProcessFiles`: Multithreading supported file processing function. Accepts: List of filenames and file paths as a tuple

    iii. Added `addFileStreams`: Multithreading supported file addition function. Accepts: List of filenames and file stream as a tuple

    iv. Added `addProcessFileStreams`: Multithreading supported combined file addition and processing function. Accepts: List of filenames and file stream as a tuple

    v. Added `generateGraphStructures`: Multithreading supported graph structure generation function. Accepts: List of filenames as contexes

    vi. Added `createGraph`: Multithreading supported graph creation function. Accepts: List of filenames as contexes

    vii. Added `getGraph`: Graph structure extraction function

    viii. Added `getGraphRetrieval`: Graph retrieval function, Accepts: Filenames as context and query

    ix. Added `createSequentialCollection`: Sequential Collection creation function. Accepts: Case-Type, Data File name as context and Weight Type

    x. Added `generateReasoning`: Sequential Collection reasoning function. Accepts: Case-Type, Data File name as context, problem space case as a JSON object string, Weight Type and Reasoning Type

<br>

14. **v0.2.2**

    i. Amended `BuildSC`: Accepts the Sequential Collection config (`scConfig`)

    ii. Amended `tikos.TikosClient.createSequentialCollection`: Accepts the Sequential Collection config (`scConfig`)

<br>

15. **v0.2.3**

    i. Added `UploadModel`: Upload trained Deep Neural Network model that need to embedded with TRP. PyTorch Based models are supported

    ii. Added `UploadModelConfig`: Upload of the configuration related to the Uploaded DNN model. Will accept the model param definition in JSON format as-well-as the model specification in YAML format

    iii. Added `UploadModelCaseData`: Upload of the selected Knowledge Cases (feature sets), that will build the initial Sequential Collection case base

    iv. Added `ProcessModel`: Process the upload DNN model with Synapses Logger embedding and dynamically creating the Sequential Collection case base

    v. Added `tikos.TikosClient.uploadEmbeddingModel`: Supports upload of the DNN model

    vi. Added `tikos.TikosClient.uploadEmbeddingConfig`: Supports upload of the DNN model configuration files

    vii. Added `tikos.TikosClient.uploadModelCaseData`: Upload of the selected Knowledge Cases (feature sets), that will build the initial Sequential Collection case base

    viii. Added `tikos.TikosClient.processEmbeddedModel`: Process the upload DNN model with Synapses Logger embedding and dynamically creating the Sequential Collection case base

<br>

16. **v0.2.4**

    i. Amended `tikos.TikosClient.generateReasoning`: Accepts base models' Neural Network Architecture types with param `nType`. Default is`0`.
    <br>
        `nType` Types:
    <br>
            **0**. Feedforward (deep) ANN <br>
            **1**. Basic Transformer based ANN <br>
            **2**. Modern Transformer based ANN

<br>

17. **v0.3.0**

    i. Added `tikos.TikosClient.generateFMProfiling`: Foundational Model Profiling function.
    <br>
    <br>
        We are pleased to announce the release of the `generateFMProfiling` function, a powerful new tool that enables evaluating and understanding the behavior of foundational models. This function provides a streamlined way to profile a models' responses to a given set of prompts.
    <br>
    <br>
        **Overview**
    <br>
        The `generateFMProfiling` function enables developers to perform targeted deep analysis of a foundational models' decisioning process. By providing a list of prompts, you can quickly build the associated Sequential Collection cases and assess the models' performance, style, and content generation on specific topics. This is essential for pruning, fine-tuning, validation, and ensuring that the model aligns with your applications' controls and requirements.
    <br>
    <br>
        **Functionality Details**
    <br>
        This functionality is designed for efficient and direct model interaction. It accepts a list of prompts (`promptTextList`) to a specified model (`modelName`) and captures its develop the Contextual Sequential Collection for future analysis. The inclusion of a keyword list allows for more granular assessment of the generated text.
    <br>
    <br>
        **Key Parameters:**
    <br>
        * **`refCaseType`**: Specifies the case type for the profiling session, allowing for context-specific evaluations.<br>
        * **`nType`**: Defines the network type to be used for the request.<br>
        * **`modelName`**: The name of the foundational model to be profiled (e.g., `meta-llama/Llama-3.2-1B`).<br>
        * **`promptTextList`**: A list of input strings to be sent to the model.<br>
        * **`keyList`**: An optional list of keywords to check for within the model's responses, enabling targeted analysis.<br>
        * **`tokenLen`**: Sets the maximum token length for the models' generated response.<br>
    <br>
        This functionality simplifies the process of gathering direct feedback from a model, making it an indispensable capability for any development lifecycle involving Foundational Models.
    <br>
    <br>
    <br>
    ii. Added `tikos.Tooling.generateFMProfileMatching`: Foundational Model Profiling Matching tool.
    <br>
    <br>
        We are introducing the `generateFMProfileMatching` tooling function, an advanced tool designed to perform profile matching for foundational models. This function allows you to compare a model's output against reference profiles to evaluate similarity and alignment.
    <br>
    <br>
        **Overview**
    <br>
        The `generateFMProfileMatching` tooling function is a sophisticated analysis tool that assesses how closely a foundational models' response traces align with a given context. By providing reference context and specifying reasoning types, you can systematically measure the models' ability to generate contextually relevant and consistent content. This is invaluable for tasks requiring high degrees of factual accuracy, style adherence, robustness, and safety compliance.
    <br>
    <br>
        **Functionality Details**
    <br>
        This tooling function orchestrates a complex workflow where a foundational model is prompted, and its decisioning traces are matched against a reference profile. It uses contextual adaptation and similarity types to perform a deep, abductive analysis of the models' behavior.
    <br>
    <br>
        **Key Parameters:**
    <br>
        * **`payloadId`**: A unique identifier for the matching task.<br>
        * **`refdoc`**: The contextual document reference(s) to improve the contextual adaptation.<br>
        * **`refCaseType`**: Specifies the case type for the profiling session, allowing for context-specific evaluations.<br>
        * **`RType `**: Defines the reasoning types for the analysis (e.g., `DEEPCAUSAL_PROFILE_PATTERN_ADV`).<br>
        * **`WType`**: Defines the processing work types for the analysis (e.g., `PROFILING`).<br>
        * **`modelName`**: The name of the foundational model to be profiled (e.g., `meta-llama/Llama-3.2-1B`).<br>
        * **`promptTextList`**: A list of input strings to be sent to the model.<br>
        * **`tokenLen`**: Sets the maximum token length for the models' generated response.<br>
        * **`nType `**: Defines the neural network type for the analysis (e.g., `2`).<br>
        * **`llmmodel` / `payloadconfig`**: Additional configuration options for specifying the LLM, and payload settings.<br>
    <br>
        By `using generateFMProfileMatching`, you can create robust, automated workflows for continuous model validation and performance monitoring.
    <br>
    <br>
    <br>
    iii. Added `tikos.Tooling.generateFMProfileGuardRailing`: Foundational Model Profiling Guard Railing tool.
    <br>
    <br>
        We are excited to introduce the `generateFMProfileGuardRailing` tooling function, a new tool designed for advanced analysis and safety monitoring of foundational models. This function serves as a "guard rail" by systematically profiling a models' behavior against a given set of prompts and configurations.
    <br>
    <br>
        **Overview**
    <br>
        The `generateFMProfileGuardRailing` function allows developers and researchers to assess how a specific foundational model, such as `meta-llama/Llama-3.2-1B`, responds to various inputs. By configuring different reasoning types, network settings, and other parameters, you can simulate diverse scenarios and analyse the models' performance, safety, and alignment in depth. This is a crucial step in ensuring model reliability and preventing unintended behavior before deployment. Moreover, this will allow business stakeholders to develop automation system controls.
    <br>
    <br>
        **Functionality Details**
    <br>
        This tool accepts a list of prompts (`promptTextList`) to a specified model (`modelName`) and evaluates its responses based on a comprehensive configuration. It is designed to be highly flexible, accepting numerous parameters to tailor each profiling session to specific needs.
    <br>
    <br>
        **Key Parameters:**
    <br>
        * **`payloadId`**: A unique identifier for the matching task.<br>
        * **`refdoc`**: The contextual document reference(s) to improve the contextual adaptation.<br>
        * **`refCaseType`**: Specifies the case type for the profiling session, allowing for context-specific evaluations.<br>
        * **`RType `**: Defines the reasoning types for the analysis (e.g., `DEEPCAUSAL_PROFILE_PATTERN_ADV`).<br>
        * **`WType`**: Defines the processing work types for the analysis (e.g., `PROFILING`).<br>
        * **`modelName`**: The name of the foundational model to be profiled (e.g., `meta-llama/Llama-3.2-1B`).<br>
        * **`promptTextList`**: A list of input strings to be sent to the model.<br>
        * **`tokenLen`**: Sets the maximum token length for the models' generated response.<br>
        * **`nType `**: Defines the neural network type for the analysis (e.g., `2`).<br>
        * **`llmmodel` / `payloadconfig`**: Additional configuration options for specifying the LLM, and payload settings.<br>
    <br>
        By leveraging `generateFMProfileGuardRailing` tooling, you can conduct targeted and repeatable experiments to build a robust profile of any foundational models' operational characteristics and deliver operational controls.
    <br>
    <br>
    <br>
