# TODO: Remove this or Fix it
import logging
import random
from .inference_api import oai_inference, vertex_claude_inference, gemini_inference
from ..prompt_templates.panel_discussion import PANEL_DISCUSSION_TEMPLATE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
MAX_ROUND = 10


class Model:
    def __init__(self, name, inference):
        self.name = name
        self.inference = inference


class AgentPanel:
    def __init__(self, model_list):
        self.model_list = model_list

    def panel_inference(self, original_question):
        panel_discussion = ""
        proposed_responses = {}
        round_number = 1
        tied_rounds = 0
        # shuffled_model_list = random.sample(self.model_list, len(self.model_list))
        shuffled_model_list = self.model_list
        final_response = None

        while round_number <= MAX_ROUND:
            previous_proposed_responses = proposed_responses.copy()
            for model in shuffled_model_list:
                prompt = self._generate_prompt(
                    model.name, original_question, panel_discussion
                )
                model_response = self._get_model_response(
                    model, prompt, proposed_responses
                )
                # if model_response:
                panel_discussion, proposed_responses = self._update_panel_discussion(
                    model, model_response, proposed_responses, panel_discussion
                )
                final_response = self._get_final_response(proposed_responses)
                if final_response:
                    return final_response
            round_number += 1

            logger.info(
                f"Round {round_number} completed. Summary of proposed responses:"
            )
            list(
                map(
                    lambda num_data: logger.info(
                        f"Response {num_data[0]}: Author: {num_data[1]['author']}, Agreements: {len(num_data[1]['agreements'])}/{len(self.model_list)}"
                    ),
                    proposed_responses.items(),
                )
            )
            tied_rounds = (
                tied_rounds + 1
                if proposed_responses == previous_proposed_responses
                else 0
            )
            if tied_rounds >= 2:
                logger.info(
                    f"Tied round {tied_rounds} - Select the most voted response. Summary of proposed responses:"
                )
                list(
                    map(
                        lambda num_data: logger.info(
                            f"Response {num_data[0]}: Author: {num_data[1]['author']}, Agreements: {len(num_data[1]['agreements'])}/{len(self.model_list)}"
                        ),
                        proposed_responses.items(),
                    )
                )
                return self._get_most_voted_response(proposed_responses)

        if round_number > MAX_ROUND:
            logger.info(f"Max rounds reached. Summary of proposed responses:")
            list(
                map(
                    lambda num_data: logger.info(
                        f"Response {num_data[0]}: Author: {num_data[1]['author']}, Agreements: {len(num_data[1]['agreements'])}/{len(self.model_list)}"
                    ),
                    proposed_responses.items(),
                )
            )
            return self._get_most_voted_response(proposed_responses)

    def _run_model_round(
        self,
        original_question,
        panel_discussion,
        proposed_responses,
        shuffled_model_list,
        round_number,
    ):
        for model in shuffled_model_list:
            prompt = self._generate_prompt(
                model.name, original_question, panel_discussion
            )
            model_response = self._get_model_response(model, prompt, proposed_responses)
            if model_response:
                panel_discussion = self._update_panel_discussion(
                    model, model_response, proposed_responses, panel_discussion
                )

        return panel_discussion

    def _generate_prompt(self, model_name, original_question, panel_discussion):
        prompt = PANEL_DISCUSSION_TEMPLATE.replace("PLACEHOLDER_MODEL_NAME", model_name)
        prompt = prompt.replace("PLACEHOLDER_ORIGINAL_QUESTION", original_question)
        prompt = prompt.replace("PLACEHOLDER_PANEL_DISCUSSION", panel_discussion)
        prompt_word = (
            "<no discussion yet. you are the first one to start. carefully analyze the question and give the proposed response. Make sure that the response meets the required format of the original question.>"
            if not panel_discussion
            else "<now give your analysis on the question and judge the previous discussion. agree on a response proposal or judge it and propose a better one. Make sure that the response meets the required format of the original question.>"
        )
        return prompt.replace("PLACEHOLDER_FINAL_PROMPT_WORD", prompt_word)

    def _update_panel_discussion(
        self, model, model_response, proposed_responses, panel_discussion
    ):
        if "START_PROPOSED_RESPONSE" in model_response:
            truncated_message = (
                "START_PROPOSED_RESPONSE"
                + model_response.split("START_PROPOSED_RESPONSE")[1]
            )
        elif "AGREE_TO_PROPOSED_RESPONSE" in model_response:
            truncated_message = (
                "AGREE_TO_PROPOSED_RESPONSE"
                + model_response.split("AGREE_TO_PROPOSED_RESPONSE")[1]
            )
        panel_discussion += f"**{model.name}**:\n{truncated_message}\n\n"

        if "START_PROPOSED_RESPONSE_" in model_response:
            response_num, proposed_response = self._extract_proposed_response(
                model_response
            )
            proposed_responses[response_num] = {
                "author": model.name,
                "response": proposed_response,
                "agreements": set([model.name]),
            }
            logger.info(f"{model.name} proposed new response {response_num}...")
        elif "AGREE_TO_PROPOSED_RESPONSE_" in model_response:
            response_num = model_response.split("AGREE_TO_PROPOSED_RESPONSE_")[1][0]
            logger.info(f"{model.name} agreed to proposal {response_num}...")
            if response_num in proposed_responses.keys():
                proposed_responses[response_num]["agreements"].add(model.name)
        return panel_discussion, proposed_responses

    def _extract_proposed_response(self, model_response):
        response_num = model_response.split("START_PROPOSED_RESPONSE_")[1].split()[0]
        proposed_response = (
            model_response.split(f"START_PROPOSED_RESPONSE_{response_num}")[1]
            .split(f"END_PROPOSED_RESPONSE_{response_num}")[0]
            .strip()
        )
        return response_num, proposed_response

    def _get_final_response(self, proposed_responses):
        if not proposed_responses:
            return None
        for response_num, data in proposed_responses.items():
            if len(data["agreements"]) == len(self.model_list):
                logger.info(
                    f"Final response was reached, proposed by {data['author']}. Summary of proposed responses:"
                )
                list(
                    map(
                        lambda num_data: logger.info(
                            f"Response {num_data[0]}: Author: {num_data[1]['author']}, Agreements: {len(num_data[1]['agreements'])}/{len(self.model_list)}"
                        ),
                        proposed_responses.items(),
                    )
                )
                return data["response"]
        return None

    def _get_most_voted_response(self, proposed_responses):
        if not proposed_responses:
            logger.info("No responses were proposed.")
            return "No consensus was reached."
        most_voted_response = max(
            proposed_responses.values(), key=lambda x: len(x["agreements"])
        )
        logger.info(
            f"Selecting the most voted response: {most_voted_response['response']} by {most_voted_response['author']}"
        )
        return most_voted_response["response"]

    def _get_model_response(self, model, prompt, proposed_responses):
        retry_attempts = 3
        for attempt in range(retry_attempts):
            try:
                logger.debug(f"Prompt for {model.name}: {prompt}")
                logger.info(f"{model.name} thinking...")
                model_response = model.inference(prompt)
                logger.debug(f"Response from {model.name}: {model_response}")

                # Check if proposed response number already exists
                if "START_PROPOSED_RESPONSE_" in model_response:
                    response_num = model_response.split("START_PROPOSED_RESPONSE_")[
                        1
                    ].split()[0]
                    if response_num in proposed_responses:
                        logger.warning(
                            f"{model.name} proposed an already existing response {response_num}. Retrying... (Attempt {attempt + 1})"
                        )
                        continue
                if (
                    "START_PROPOSED_RESPONSE_" in model_response
                    or "AGREE_TO_PROPOSED_RESPONSE_" in model_response
                ):
                    return model_response
                else:
                    logger.warning(
                        f"{model.name} response did not contain expected keywords. Retrying... (Attempt {attempt + 1})"
                    )
            except Exception as e:
                logger.error(
                    f"Error during {model.name} inference: {e}. Retrying... (Attempt {attempt + 1})"
                )
        logger.error(
            f"{model.name} failed to provide a valid response after {retry_attempts} attempts."
        )
        return None


def build_agent_panel():
    # model_list = [
    #     Model("Gemini", gemini_inference),
    #     Model("Claude", claude_inference),
    #     Model("OAI", oai_inference)
    # ]
    model_list = [
        Model("Agent_1", vertex_claude_inference),
        Model("Agent_2", gemini_inference),
        Model("Agent_3", oai_inference),
    ]
    return AgentPanel(model_list)


agent_panel = build_agent_panel()
panel_inference = agent_panel.panel_inference

if __name__ == "__main__":
    RESET = "\033[0m"
    YELLOW = "\033[33m"
    GREEN = "\033[32m"
    model_list = [
        Model("Gemini", gemini_inference),
        Model("Claude", vertex_claude_inference),
        Model("OAI", oai_inference),
    ]

    agent_panel = AgentPanel(model_list)
    try:
        while True:
            print(
                f"Enter the question for the panel discussion (press Enter twice to submit): {YELLOW}"
            )
            original_question = ""
            while True:
                line = input()
                if line == "":
                    break
                original_question += line + "\n"
            print(f"{RESET}")
            response = agent_panel.panel_inference(original_question.strip())
            print(f"{GREEN}{response}{RESET}")
    except KeyboardInterrupt:
        print(f"{YELLOW}\nExiting interactive chat mode.{RESET}")
