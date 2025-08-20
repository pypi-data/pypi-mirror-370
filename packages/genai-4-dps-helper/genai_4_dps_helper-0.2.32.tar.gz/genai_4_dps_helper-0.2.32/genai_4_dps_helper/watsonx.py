from typing import Dict, List

from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import Embeddings, ModelInference

from genai_4_dps_helper.base_obj import BaseObj


class IBMWatsonx(BaseObj):
    """A wrapper class to ibm_wastonx_ai the simplifies the code required to prompt watsonx"""

    def __init__(
        self,
        model_name,
        watsonx_params: Dict,
        project_id: str,
        credentials: Credentials,
    ) -> None:
        """Create the client and the model,

        Args:
            model_name (_type_): The model name to be accessed for example: meta-llama/llama-3-1-70b-instruct
            watsonx_params (Dict): Additional parameters to be passed to the model
            project_id (str): The project id within wastonx.ai to connect to
            credentials (Credentials): The ibm_wastonx_ai Credentials for accessing watsonx.ai

            from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
            parameters: Dict = {
                GenParams.DECODING_METHOD: DecodingMethods.SAMPLE.value,
                GenParams.MIN_NEW_TOKENS: 0,
                GenParams.MAX_NEW_TOKENS: 1000,
                GenParams.TEMPERATURE: 0.7,
                GenParams.TOP_P: 1,
                GenParams.TOP_K: 50,
                GenParams.RANDOM_SEED: 2973559815,
                GenParams.REPETITION_PENALTY: 1,
            }
        """
        super(IBMWatsonx, self).__init__()
        self.__model_name: str = model_name
        self.__params: Dict = watsonx_params
        self.__project_id: str = project_id
        self.__credentials: Credentials = credentials
        self.__client: APIClient = self.__get_watson_client()
        self.__model: ModelInference = self.__load_model()

    @property
    def model(self):
        return self.__model

    def list_embedding_models(self):
        """List the available EmbeddingModels"""
        self.__client.foundation_models.EmbeddingModels.show()

    def list_chat_models(self):
        """List the available ChatModels"""
        self.__client.foundation_models.ChatModels.show()

    def send_to_watsonxai(self, prompts: List[str]) -> List[str]:
        gen_texts = self.__model.generate_text(prompts)
        return gen_texts

    def __get_watson_client(self) -> APIClient:
        # creds: Credentials = self.__get_watson_creds()
        client = client = APIClient(self.__credentials)
        client.set.default_project(self.__project_id)
        return client

    # def __get_watson_creds(self) -> Credentials:
    # api_key = os.getenv("WML_WATSONX_AI_API_KEY", None)
    # ibm_cloud_url = os.getenv("WML_WATSONX_AI_ENDPOINT", None)
    # if api_key is None or ibm_cloud_url is None:
    #     print(
    #         "Ensure you copied the .env file that you created earlier into the same directory as this notebook"
    #     )
    # else:
    #     creds = Credentials(url=ibm_cloud_url, api_key=api_key)
    # return creds

    def __load_model(self):
        """
        helper function for sending prompts and params to Watsonx.ai

        Args:

            decoding:str Watsonx.ai parameter "sample" or "greedy"
            max_new_tok:int Watsonx.ai parameter for max new tokens/response returned
            temp:float Watsonx.ai parameter for temperature (range 0>2)

        Returns: Model
        """
        # creds: Credentials = self.__get_watson_creds()
        model = ModelInference(
            model_id=self.__model_name,
            params=self.__params,
            credentials=self.__credentials,
            project_id=self.__project_id,
        )
        return model


# Need to define an Embedding Function for the documents
class WatsonxEmbeddingFunction(BaseObj):
    """An embedding function to enable the embeddings against the passed in embedding_model"""

    def __init__(self, embedding_model: Embeddings):
        """Creates a watsonxEmbeddingFunction

        Args:
            embedding_model (Embeddings): The Embedding model to use
        """
        super(WatsonxEmbeddingFunction, self).__init__()
        self.__the_model = embedding_model

    def embed_documents(self, document_list: List[str]) -> List[List[float]]:
        return self.__the_model.embed_documents(document_list)

    def embed_query(self, query) -> List[float]:
        return self.__the_model.embed_query(query)
