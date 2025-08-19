import logging
from anges.agents.agent_utils.agent_factory import AgentFactory, AgentType, AgentConfig
from anges.utils.event_storage_service import event_storage_service as event_storage
from anges.config import config

# Configure logging

logger = logging.getLogger(__name__)

def run_agent_task(
    message,
    event_stream=None,
    message_queue=None,
    interrupt_flags=None,
    chat_id=None,
    cmd_init_dir=None,
    model=None,
    prefix_cmd="",
    agent_type="task_executor",
    notes=[],
):
    """
    Run an agent task with the given parameters.
    """
    # Import active_tasks here to avoid circular imports
    from anges.web_interface.web_interface import active_tasks
    
    # Configure logging to use QueueHandler
    agent_logger = logging.getLogger("anges.agents.agent_message_logger")

    # Create a handler that puts log messages into the queue
    class QueueHandler(logging.Handler):
        def emit(self, record):
            if record.levelno == logging.INFO and message_queue:
                logger.debug(f"Queue handler received message: {record.getMessage()}")
                # message_queue.put(self.format(record))

    # Create a direct message handler function that puts messages directly into the queue
    def direct_message_handler(message):
        if message_queue:
            logger.debug(f"Direct message handler received message: {message}")
            message_queue.put(message)

    # Set up interrupt check function
    def check_interrupt():
        if interrupt_flags and chat_id in interrupt_flags:
            return interrupt_flags[chat_id]
        return False

    # Add queue handler to logger if message_queue is provided
    if message_queue:
        queue_handler = QueueHandler()
        queue_handler.setFormatter(logging.Formatter("%(message)s"))
        agent_logger.addHandler(queue_handler)
        agent_logger.setLevel(logging.DEBUG)

    try:
        # Create agent configuration
        agent_config = AgentConfig(
            agent_type=agent_type,
            event_stream=event_stream,
            cmd_init_dir=cmd_init_dir,
            model=model,
            prefix_cmd=prefix_cmd,
            interrupt_check=check_interrupt,
            auto_entitle=True,
            remaining_recursive_depth=3 if agent_type == "orchestrator" else None,
            max_consecutive_actions_to_summarize=config.agents.orchestrator.max_consecutive_actions_to_summarize if agent_type == "orchestrator" else None,
            notes=notes,
        )
        
        # Create the agent using the centralized factory
        factory = AgentFactory()
        agent = factory.create_agent(agent_config)
        
        logger.debug(f"Using {agent_type} agent created by AgentFactory")

        # Register the direct message handler with the agent
        if message_queue:
            agent.message_handlers.append(direct_message_handler)

        # Run the agent with the task
        event_stream = agent.run_with_new_request(
            task_description=message,
            event_stream=event_stream,
        )
        
        logger.debug("Agent task completed")
        event_storage.save(event_stream)  # Save after successful completion
        
        if message_queue:
            message_queue.put("STREAM_COMPLETE")
        
        # Mark the task as complete
        if chat_id is not None:
            active_tasks[chat_id] = False
            logger.debug(f"Marked chat {chat_id} as having completed its task")
        
        return event_stream
    
    except Exception as e:
        logger.error(f"Agent task failed: {e}. Anget Config:\n{agent.agent_config}", exc_info=True)
        
        # Mark the task as complete even if it failed
        if chat_id is not None:
            active_tasks[chat_id] = False
            logger.debug(f"Marked chat {chat_id} as having completed its task (after error)")
        
        raise
    
    finally:
        # Clean up interrupt flag
        if interrupt_flags and chat_id in interrupt_flags:
            del interrupt_flags[chat_id]

        # Remove the queue handler to prevent memory leaks
        if message_queue and agent_logger.handlers:
            for handler in agent_logger.handlers[:]:
                if isinstance(handler, QueueHandler):
                    agent_logger.removeHandler(handler)
