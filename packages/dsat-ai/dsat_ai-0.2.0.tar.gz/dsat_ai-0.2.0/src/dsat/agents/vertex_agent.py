import logging
from .agent import Agent, AgentConfig
from .agent_logger import CallTimer

try:
    import vertexai
    from vertexai.generative_models import GenerativeModel

    VERTEX_AI_AVAILABLE = True
except ImportError:
    vertexai = None
    GenerativeModel = None
    VERTEX_AI_AVAILABLE = False


class GoogleVertexAIAgent(Agent):
    """
    Google Vertex AI LLM agent.
    """

    def __init__(self, config: AgentConfig = None, project_id: str = None, location: str = None, model: str = None, logger: logging.Logger = None, prompts_dir = None):
        # Support both old API (project_id, location, model) and new API (config)
        if config is None:
            # Backward compatibility - create config from parameters
            if project_id is None or model is None:
                raise ValueError("Either config must be provided, or both project_id and model must be provided")
                
            config = AgentConfig(
                agent_name="vertex",
                model_provider="google",
                model_family="gemini", 
                model_version=model,
                prompt="default:v1",
                provider_auth={"project_id": project_id, "location": location or "us-central1"}
            )
        else:
            # Use provided config, but allow parameter overrides for backward compatibility
            if project_id is not None:
                config.provider_auth["project_id"] = project_id
            if location is not None:
                config.provider_auth["location"] = location
        
        # Use provided logger or create a default one
        if logger is None:
            logger = logging.getLogger(__name__)
        
        super().__init__(config, logger, prompts_dir)
        
        if not VERTEX_AI_AVAILABLE:
            raise ImportError("google-cloud-aiplatform package is required for Google Vertex AI support")

        # Get auth parameters from config
        project_id_from_config = config.provider_auth.get("project_id")
        location_from_config = config.provider_auth.get("location", "us-central1")
        
        if not project_id_from_config:
            raise ValueError("project_id is required in provider_auth for GoogleVertexAIAgent")

        vertexai.init(project=project_id_from_config, location=location_from_config)
        self.client = GenerativeModel(config.model_version)

    def invoke(self, user_prompt: str, system_prompt: str = None) -> str:
        # Use model parameters from config, with defaults
        model_params = self.config.model_parameters or {}
        temperature = model_params.get("temperature", 0.3)
        max_output_tokens = model_params.get("max_output_tokens", 20000)
        
        # Use provided system prompt or load from prompt manager
        if system_prompt is None:
            system_prompt = self.get_system_prompt()
        
        # Combine system and user prompts for Vertex AI
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
        else:
            full_prompt = user_prompt
        
        # Prepare request data for logging
        request_data = {
            "user_prompt": user_prompt,
            "system_prompt": system_prompt,
            "full_prompt": full_prompt,
            "model_parameters": {
                "temperature": temperature,
                "max_output_tokens": max_output_tokens
            }
        }

        try:
            with CallTimer() as timer:
                response = self.client.generate_content(
                    full_prompt,
                    generation_config={
                        "temperature": temperature,
                        "max_output_tokens": max_output_tokens,
                    }
                )

            self.logger.debug(f"Vertex AI raw response: {response.text}")
            self.logger.debug(f".. response: {len(response.text)} bytes / {len(response.text.split())} words")

            # Prepare response data for logging
            response_data = {
                "content": response.text,
                "tokens_used": {
                    "input": getattr(response.usage_metadata, 'prompt_token_count', None) if hasattr(response, 'usage_metadata') else None,
                    "output": getattr(response.usage_metadata, 'candidates_token_count', None) if hasattr(response, 'usage_metadata') else None
                }
            }
            
            # Log the LLM call if logger is configured
            if self.call_logger:
                self.call_logger.log_llm_call(
                    request_data=request_data,
                    response_data=response_data,
                    duration_ms=timer.duration_ms,
                    model_provider=self.config.model_provider,
                    model_version=self.config.model_version
                )

            return response.text

        except Exception as e:
            # Log errors
            if self.call_logger:
                self.call_logger.log_llm_call(
                    request_data=request_data,
                    response_data={"error": str(e), "error_type": type(e).__name__},
                    duration_ms=timer.duration_ms if 'timer' in locals() else 0,
                    model_provider=self.config.model_provider,
                    model_version=self.config.model_version
                )
            
            self.logger.error(f"Vertex AI API error: {str(e)}")
            raise

    @property
    def model(self) -> str:
        return self.config.model_version

