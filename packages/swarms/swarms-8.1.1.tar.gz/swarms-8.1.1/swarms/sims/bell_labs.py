"""
Bell Labs Research Simulation with Physicist Agents

This simulation creates specialized AI agents representing famous physicists
from the Bell Labs era, including Oppenheimer, von Neumann, Feynman, Einstein,
and others. The agents work together in a collaborative research environment
following a structured workflow: task -> Oppenheimer (planning) -> physicist discussion
-> code implementation -> results analysis -> repeat for n loops.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from functools import lru_cache

from loguru import logger

from swarms.structs.agent import Agent
from swarms.structs.conversation import Conversation
from swarms.structs.majority_voting import MajorityVoting
from swarms.utils.history_output_formatter import (
    history_output_formatter,
)


@dataclass
class ResearchPhase:
    """Represents a phase of the research process."""

    phase_name: str
    description: str
    status: str = "pending"
    output: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BellLabsSwarm:
    """
    Bell Labs Research Simulation Swarm

    Simulates the collaborative research environment of Bell Labs with famous physicists
    working together on complex research questions. The workflow follows:

    1. Task is presented to the team
    2. Oppenheimer creates a research plan
    3. Physicists discuss and vote on approaches using majority voting
    4. Code implementation agent tests the theory
    5. Results are analyzed and fed back to the team
    6. Process repeats for n loops with iterative refinement
    """

    def __init__(
        self,
        name: str = "Bell Labs Research Team",
        description: str = "A collaborative research environment simulating Bell Labs physicists",
        max_loops: int = 1,
        verbose: bool = True,
        model_name: str = "gpt-4o-mini",
        random_model_name: bool = False,
        output_type: str = "str-all-except-first",
        **kwargs,
    ):
        """
        Initialize the Bell Labs Research Swarm.

        Args:
            name: Name of the swarm
            description: Description of the swarm's purpose
            max_loops: Number of research iteration loops
            verbose: Whether to enable verbose logging
            model_name: Model to use for all agents
            **kwargs: Additional arguments passed to BaseSwarm
        """
        self.name = name
        self.description = description
        self.max_loops = max_loops
        self.verbose = verbose
        self.model_name = model_name
        self.kwargs = kwargs
        self.random_model_name = random_model_name
        self.output_type = output_type

        self.conversation = Conversation()

        # Create the physicist agents
        self.agents = self._create_physicist_agents(model_name)

        # Set up specialized agents
        self.oppenheimer = self._get_agent_by_name(
            "J. Robert Oppenheimer"
        )
        self.code_implementer = self._get_agent_by_name(
            "Code Implementer"
        )

        self.physicists = [
            agent
            for agent in self.agents
            if agent.agent_name != "J. Robert Oppenheimer"
            and agent.agent_name != "Code Implementer"
        ]

        logger.info(
            f"Bell Labs Research Team initialized with {len(self.agents)} agents"
        )

    @lru_cache(maxsize=1)
    def _create_physicist_agents(
        self, model_name: str
    ) -> List[Agent]:
        """
        Create specialized agents for each physicist.

        Args:
            model_name: Model to use for all agents

        Returns:
            List of configured physicist agents
        """
        physicists_data = {
            "J. Robert Oppenheimer": {
                "role": "Research Director & Theoretical Physicist",
                "expertise": [
                    "Nuclear physics",
                    "Quantum mechanics",
                    "Research coordination",
                    "Strategic planning",
                    "Team leadership",
                ],
                "background": "Director of the Manhattan Project, expert in quantum mechanics and nuclear physics",
                "system_prompt": """You are J. Robert Oppenheimer, the brilliant theoretical physicist and research director.
                
                Your role is to:
                1. Analyze complex research questions and break them down into manageable components
                2. Create comprehensive research plans with clear objectives and methodologies
                3. Coordinate the research team and ensure effective collaboration
                4. Synthesize findings from different physicists into coherent conclusions
                5. Guide the research process with strategic insights and theoretical frameworks
                
                You excel at:
                - Identifying the core theoretical challenges in any research question
                - Designing experimental approaches that test fundamental principles
                - Balancing theoretical rigor with practical implementation
                - Fostering interdisciplinary collaboration between specialists
                - Maintaining focus on the most promising research directions
                
                When creating research plans, be thorough, systematic, and consider multiple approaches.
                Always emphasize the theoretical foundations and experimental validation of any proposed solution.""",
            },
            "John von Neumann": {
                "role": "Mathematical Physicist & Computer Scientist",
                "expertise": [
                    "Mathematical physics",
                    "Computer architecture",
                    "Game theory",
                    "Quantum mechanics",
                    "Numerical methods",
                ],
                "background": "Pioneer of computer science, game theory, and mathematical physics",
                "system_prompt": """You are John von Neumann, the brilliant mathematical physicist and computer scientist.
                
                Your approach to research questions involves:
                1. Mathematical rigor and formal mathematical frameworks
                2. Computational and algorithmic solutions to complex problems
                3. Game theory and strategic analysis of research approaches
                4. Numerical methods and computational physics
                5. Bridging abstract theory with practical implementation
                
                You excel at:
                - Formulating problems in precise mathematical terms
                - Developing computational algorithms and numerical methods
                - Applying game theory to optimize research strategies
                - Creating mathematical models that capture complex phenomena
                - Designing efficient computational approaches to physical problems
                
                When analyzing research questions, focus on mathematical foundations, computational feasibility,
                and the development of rigorous theoretical frameworks that can be implemented and tested.""",
            },
            "Richard Feynman": {
                "role": "Theoretical Physicist & Problem Solver",
                "expertise": [
                    "Quantum electrodynamics",
                    "Particle physics",
                    "Problem-solving methodology",
                    "Intuitive physics",
                    "Experimental design",
                ],
                "background": "Nobel laureate in physics, known for intuitive problem-solving and quantum electrodynamics",
                "system_prompt": """You are Richard Feynman, the brilliant theoretical physicist and master problem solver.
                
                Your research methodology involves:
                1. Intuitive understanding of complex physical phenomena
                2. Creative problem-solving approaches that cut through complexity
                3. Experimental design that tests fundamental principles
                4. Clear communication of complex ideas through analogies and examples
                5. Focus on the most essential aspects of any research question
                
                You excel at:
                - Finding elegant solutions to seemingly intractable problems
                - Designing experiments that reveal fundamental truths
                - Communicating complex physics in accessible terms
                - Identifying the core physics behind any phenomenon
                - Developing intuitive models that capture essential behavior
                
                When approaching research questions, look for the simplest, most elegant solutions.
                Focus on the fundamental physics and design experiments that test your understanding directly.""",
            },
            "Albert Einstein": {
                "role": "Theoretical Physicist & Conceptual Innovator",
                "expertise": [
                    "Relativity theory",
                    "Quantum mechanics",
                    "Conceptual physics",
                    "Thought experiments",
                    "Fundamental principles",
                ],
                "background": "Revolutionary physicist who developed relativity theory and influenced quantum mechanics",
                "system_prompt": """You are Albert Einstein, the revolutionary theoretical physicist and conceptual innovator.
                
                Your research approach involves:
                1. Deep conceptual thinking about fundamental physical principles
                2. Thought experiments that reveal the essence of physical phenomena
                3. Questioning established assumptions and exploring new paradigms
                4. Focus on the most fundamental and universal aspects of physics
                5. Intuitive understanding of space, time, and the nature of reality
                
                You excel at:
                - Identifying the conceptual foundations of any physical theory
                - Developing thought experiments that challenge conventional wisdom
                - Finding elegant mathematical descriptions of physical reality
                - Questioning fundamental assumptions and exploring alternatives
                - Developing unified theories that explain diverse phenomena
                
                When analyzing research questions, focus on the conceptual foundations and fundamental principles.
                Look for elegant, unified explanations and be willing to challenge established paradigms.""",
            },
            "Enrico Fermi": {
                "role": "Experimental Physicist & Nuclear Scientist",
                "expertise": [
                    "Nuclear physics",
                    "Experimental physics",
                    "Neutron physics",
                    "Statistical physics",
                    "Practical applications",
                ],
                "background": "Nobel laureate known for nuclear physics, experimental work, and the first nuclear reactor",
                "system_prompt": """You are Enrico Fermi, the brilliant experimental physicist and nuclear scientist.
                
                Your research methodology involves:
                1. Rigorous experimental design and execution
                2. Practical application of theoretical principles
                3. Statistical analysis and probability in physics
                4. Nuclear physics and particle interactions
                5. Bridging theory with experimental validation
                
                You excel at:
                - Designing experiments that test theoretical predictions
                - Applying statistical methods to physical problems
                - Developing practical applications of fundamental physics
                - Nuclear physics and particle physics experiments
                - Creating experimental setups that reveal new phenomena
                
                When approaching research questions, focus on experimental design and practical implementation.
                Emphasize the importance of experimental validation and statistical analysis in physics research.""",
            },
            "Code Implementer": {
                "role": "Computational Physicist & Code Developer",
                "expertise": [
                    "Scientific computing",
                    "Physics simulations",
                    "Data analysis",
                    "Algorithm implementation",
                    "Numerical methods",
                ],
                "background": "Specialized in implementing computational solutions to physics problems",
                "system_prompt": """You are a specialized computational physicist and code developer.
                
                Your responsibilities include:
                1. Implementing computational solutions to physics problems
                2. Developing simulations and numerical methods
                3. Analyzing data and presenting results clearly
                4. Testing theoretical predictions through computation
                5. Providing quantitative analysis of research findings
                
                You excel at:
                - Writing clear, efficient scientific code
                - Implementing numerical algorithms for physics problems
                - Data analysis and visualization
                - Computational optimization and performance
                - Bridging theoretical physics with computational implementation
                
                When implementing solutions, focus on:
                - Clear, well-documented code
                - Efficient numerical algorithms
                - Comprehensive testing and validation
                - Clear presentation of results and analysis
                - Quantitative assessment of theoretical predictions""",
            },
        }

        agents = []
        for name, data in physicists_data.items():
            agent = Agent(
                agent_name=name,
                system_prompt=data["system_prompt"],
                model_name=model_name,
                random_model_name=self.random_model_name,
                max_loops=1,
                dynamic_temperature_enabled=True,
                dynamic_context_window=True,
            )
            agents.append(agent)

        return agents

    def _get_agent_by_name(self, name: str) -> Optional[Agent]:
        """Get an agent by name."""
        for agent in self.agents:
            if agent.agent_name == name:
                return agent
        return None

    def run(
        self, task: str, img: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run the Bell Labs research simulation.

        Args:
            task: The research question or task to investigate

        Returns:
            Dictionary containing the research results, process history, and full conversation
        """
        logger.info(f"Starting Bell Labs research on: {task}")

        # Add initial task to conversation history
        self.conversation.add(
            "Research Coordinator", f"Initial Research Task: {task}"
        )

        # Oppenheimer
        oppenheimer_plan = self.oppenheimer.run(task=task, img=img)

        self.conversation.add(
            self.oppenheimer.agent_name,
            f"Research Plan: {oppenheimer_plan}",
        )

        # Discussion

        # Physicists
        physicist_discussion = self._conduct_physicist_discussion(
            task, oppenheimer_plan
        )

        # Add to conversation history
        self.conversation.add(
            "Group Discussion", physicist_discussion
        )

        # Now implement the solution
        implementation_results = self._implement_and_test_solution(
            history=self.conversation.get_str()
        )

        # Add to conversation history
        self.conversation.add(
            self.code_implementer.agent_name, implementation_results
        )

        return history_output_formatter(
            conversation=self.conversation, type="str"
        )

    def _create_research_plan(
        self, task: str, loop_number: int
    ) -> str:
        """
        Have Oppenheimer create a research plan.

        Args:
            task: Research task
            loop_number: Current loop number

        Returns:
            Research plan from Oppenheimer
        """
        prompt = f"""
        Research Task: {task}
        
        Loop Number: {loop_number + 1}
        
        As J. Robert Oppenheimer, create a comprehensive research plan for this task.
        
        Your plan should include:
        1. Clear research objectives and hypotheses
        2. Theoretical framework and approach
        3. Specific research questions to investigate
        4. Methodology for testing and validation
        5. Expected outcomes and success criteria
        6. Timeline and milestones
        7. Resource requirements and team coordination
        
        Provide a detailed, actionable plan that the research team can follow.
        """

        plan = self.oppenheimer.run(prompt)
        return plan

    def _conduct_physicist_discussion(
        self, task: str, history: str
    ) -> Dict[str, Any]:
        """
        Conduct a discussion among physicists using majority voting.

        Args:
            task: Research task
            plan: Oppenheimer's research plan
            loop_number: Current loop number

        Returns:
            Results of the physicist discussion and voting
        """
        # Create discussion prompt
        discussion_prompt = f"""
        {history}
        
        Current Research Task: {task}
        
        As a team of physicists, discuss this research plan and approach. Consider:
        
        1. Theoretical soundness of the proposed approach
        2. Feasibility of implementation and testing
        3. Potential challenges and alternative solutions
        4. Expected outcomes and limitations
        5. Recommendations for improvement
        
        Provide your analysis and recommendations. Be specific about:
        - What aspects of the plan you support
        - What concerns you have
        - What alternatives you suggest
        - How to proceed with implementation
        
        Focus on the physics and scientific merit of the approach.
        """

        # Run discussion with majority voting
        majority_voting = MajorityVoting(
            name="Physicist Discussion",
            description="Discussion and voting among physicists",
            agents=self.physicists,
            output_type="str-all-except-first",
            max_loops=1,
        )

        discussion_results = majority_voting.run(discussion_prompt)

        return discussion_results

    def _implement_and_test_solution(
        self,
        history: str,
    ) -> Dict[str, Any]:
        """
        Implement and test the proposed solution.

        Args:
            task: Research task
            plan: Research plan
            discussion_results: Results from physicist discussion
            loop_number: Current loop number

        Returns:
            Implementation and testing results
        """
        implementation_prompt = f"""
        {history}
        
        As the Code Implementer, your task is to:
        
        1. Implement a computational solution based on the research plan
        2. Test the theoretical predictions through simulation or calculation
        3. Analyze the results and provide quantitative assessment
        4. Identify any discrepancies between theory and implementation
        5. Suggest improvements or next steps
        
        Provide:
        - Clear description of your implementation approach
        - Code or algorithm description
        - Test results and analysis
        - Comparison with theoretical predictions
        - Recommendations for further investigation
        
        Focus on practical implementation and quantitative results.
        """

        implementation_results = self.code_implementer.run(
            implementation_prompt
        )

        return implementation_results

    def _analyze_results(
        self, implementation_results: Dict[str, Any], loop_number: int
    ) -> str:
        """
        Analyze the results and provide team review.

        Args:
            implementation_results: Results from implementation phase
            loop_number: Current loop number

        Returns:
            Analysis and recommendations
        """
        analysis_prompt = f"""
        Implementation Results: {implementation_results}
        
        Loop Number: {loop_number + 1}
        
        As the research team, analyze these results and provide:
        
        1. Assessment of whether the implementation supports the theoretical predictions
        2. Identification of any unexpected findings or discrepancies
        3. Evaluation of the methodology and approach
        4. Recommendations for the next research iteration
        5. Insights gained from this round of investigation
        
        Consider:
        - What worked well in this approach?
        - What challenges or limitations were encountered?
        - How can the research be improved in the next iteration?
        - What new questions or directions have emerged?
        
        Provide a comprehensive analysis that will guide the next research phase.
        """

        # Use majority voting for team analysis
        majority_voting = MajorityVoting(
            name="Results Analysis",
            description="Team analysis of implementation results",
            agents=self.agents,
            verbose=self.verbose,
            output_type="str-all-except-first",
            max_loops=1,
        )

        analysis_results = majority_voting.run(analysis_prompt)

        return analysis_results

    def _refine_task_for_next_iteration(
        self, current_task: str, loop_results: Dict[str, Any]
    ) -> str:
        """
        Refine the task for the next research iteration.

        Args:
            current_task: Current research task
            loop_results: Results from the current loop

        Returns:
            Refined task for next iteration
        """
        refinement_prompt = f"""
        Current Research Task: {current_task}
        
        Results from Current Loop: {loop_results}
        
        Based on the findings and analysis from this research loop, refine the research task for the next iteration.
        
        Consider:
        - What new questions have emerged?
        - What aspects need deeper investigation?
        - What alternative approaches should be explored?
        - What specific hypotheses should be tested?
        
        Provide a refined, focused research question that builds upon the current findings
        and addresses the most important next steps identified by the team.
        """

        # Use Oppenheimer to refine the task
        refined_task = self.oppenheimer.run(refinement_prompt)

        # Add task refinement to conversation history
        self.conversation.add(
            "J. Robert Oppenheimer",
            f"Task Refined for Next Iteration: {refined_task}",
        )

        return refined_task

    def _generate_final_conclusion(
        self, research_results: Dict[str, Any]
    ) -> str:
        """
        Generate a final conclusion summarizing all research findings.

        Args:
            research_results: Complete research results from all loops

        Returns:
            Final research conclusion
        """
        conclusion_prompt = f"""
        Complete Research Results: {research_results}
        
        As J. Robert Oppenheimer, provide a comprehensive final conclusion for this research project.
        
        Your conclusion should:
        1. Summarize the key findings from all research loops
        2. Identify the most significant discoveries or insights
        3. Evaluate the success of the research approach
        4. Highlight any limitations or areas for future investigation
        5. Provide a clear statement of what was accomplished
        6. Suggest next steps for continued research
        
        Synthesize the work of the entire team and provide a coherent narrative
        of the research journey and its outcomes.
        """

        final_conclusion = self.oppenheimer.run(conclusion_prompt)
        return final_conclusion


# Example usage function
def run_bell_labs_research(
    research_question: str,
    max_loops: int = 3,
    model_name: str = "gpt-4o-mini",
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    Run a Bell Labs research simulation.

    Args:
        research_question: The research question to investigate
        max_loops: Number of research iteration loops
        model_name: Model to use for all agents
        verbose: Whether to enable verbose logging

    Returns:
        Complete research results and findings
    """
    bell_labs = BellLabsSwarm(
        max_loops=max_loops, verbose=verbose, model_name=model_name
    )

    results = bell_labs.run(research_question)
    return results


# if __name__ == "__main__":
#     # Example research question
#     research_question = """
#     Investigate the feasibility of quantum computing for solving complex optimization problems.
#     Consider both theoretical foundations and practical implementation challenges.
#     """

#     print("Starting Bell Labs Research Simulation...")
#     print(f"Research Question: {research_question}")
#     print("-" * 80)

#     results = run_bell_labs_research(
#         research_question=research_question,
#         max_loops=2,
#         verbose=True
#     )

#     print("\n" + "=" * 80)
#     print("RESEARCH SIMULATION COMPLETED")
#     print("=" * 80)

#     print(f"\nFinal Conclusion:\n{results['final_conclusion']}")

#     print(f"\nResearch completed in {len(results['research_history'])} loops.")
#     print("Check the results dictionary for complete research details.")
