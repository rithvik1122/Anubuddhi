"""
Analyzer Agent for evaluating quantum experiments and extracting insights.
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
from dataclasses import dataclass

from .base_agent import BaseAgent, AgentMessage, AgentRole, MessageType, AgentCapability
from ..quantum import QuantumExperiment, ExperimentResults, QuantumSimulator

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Container for analysis results."""
    experiment_id: str
    analysis_type: str
    metrics: Dict[str, float]
    insights: List[str]
    recommendations: List[str]
    confidence: float
    timestamp: datetime


class AnalyzerAgent(BaseAgent):
    """
    Agent responsible for analyzing quantum experiment results.
    
    The Analyzer Agent:
    - Evaluates experiment performance using multiple metrics
    - Extracts insights from experimental data
    - Identifies patterns and anomalies
    - Provides recommendations for improvements
    - Builds knowledge base of experimental insights
    """
    
    def __init__(self, agent_id: str = "analyzer_001", **kwargs):
        """Initialize the Analyzer Agent."""
        super().__init__(
            agent_id=agent_id,
            role=AgentRole.ANALYZER,
            name="Quantum Experiment Analyzer",
            description="Analyzes quantum experiments and extracts actionable insights",
            **kwargs
        )
        
        # Analysis configuration
        self.analysis_threshold = getattr(self.config, "analysis_threshold", 0.1)
        self.insight_confidence_threshold = getattr(self.config, "insight_confidence", 0.7)
        self.enable_deep_analysis = getattr(self.config, "deep_analysis", True)
        
        # Metrics and evaluation criteria
        self.figure_of_merit_weights = getattr(self.config, "fom_weights", {
            "fidelity": 0.3,
            "success_probability": 0.2,
            "fisher_information": 0.2,
            "execution_time": 0.1,
            "resource_efficiency": 0.2
        })
        
        # Knowledge base for insights
        self.analysis_history = []
        self.pattern_database = {}
        self.anomaly_detectors = self._initialize_anomaly_detectors()
        
        logger.info("Analyzer Agent initialized")
    
    def get_capabilities(self) -> List[AgentCapability]:
        """Return Analyzer Agent capabilities."""
        return [
            AgentCapability(
                name="experiment_evaluation",
                description="Comprehensive evaluation of experiment results",
                input_types=["experiment_results", "evaluation_criteria"],
                output_types=["performance_metrics", "evaluation_report"]
            ),
            AgentCapability(
                name="pattern_analysis",
                description="Identify patterns in experimental data",
                input_types=["experiment_data", "pattern_types"],
                output_types=["patterns", "correlations"]
            ),
            AgentCapability(
                name="insight_extraction",
                description="Extract actionable insights from results",
                input_types=["analysis_results", "domain_knowledge"],
                output_types=["insights", "recommendations"]
            ),
            AgentCapability(
                name="comparative_analysis",
                description="Compare multiple experiments",
                input_types=["experiment_list", "comparison_criteria"],
                output_types=["comparison_report", "rankings"]
            ),
            AgentCapability(
                name="anomaly_detection",
                description="Detect anomalies in experimental data",
                input_types=["experimental_data", "baseline_data"],
                output_types=["anomalies", "anomaly_scores"]
            )
        ]
    
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process incoming analysis requests."""
        content = message.content
        action = content.get("action", "")
        
        try:
            if action == "analyze_experiment":
                result = await self._analyze_experiment(content)
            elif action == "compare_experiments":
                result = await self._compare_experiments(content)
            elif action == "extract_insights":
                result = await self._extract_insights(content)
            elif action == "detect_anomalies":
                result = await self._detect_anomalies(content)
            elif action == "analyze_patterns":
                result = await self._analyze_patterns(content)
            elif action == "evaluate_performance":
                result = await self._evaluate_performance(content)
            else:
                result = {"error": f"Unknown action: {action}"}
            
            return await self.send_message(
                receiver_id=message.sender_id,
                message_type=MessageType.RESPONSE,
                content=result,
                conversation_id=message.conversation_id
            )
        
        except Exception as e:
            logger.error(f"Analyzer Agent error: {e}")
            return await self.send_message(
                receiver_id=message.sender_id,
                message_type=MessageType.ERROR,
                content={"error": str(e)},
                conversation_id=message.conversation_id
            )
    
    async def _analyze_experiment(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive analysis of a single experiment.
        
        Args:
            request: Analysis request containing experiment results
        
        Returns:
            Detailed analysis report
        """
        experiment_results = request.get("experiment_results", {})
        analysis_type = request.get("analysis_type", "comprehensive")
        
        experiment_id = experiment_results.get("experiment_id", "unknown")
        logger.info(f"Analyzing experiment {experiment_id}")
        
        # Extract key metrics
        figures_of_merit = experiment_results.get("figures_of_merit", {})
        execution_time = experiment_results.get("execution_time", 0.0)
        success_probability = experiment_results.get("success_probability", 0.0)
        
        # Calculate composite performance score
        performance_score = self._calculate_performance_score(figures_of_merit, execution_time, success_probability)
        
        # Analyze individual metrics
        metric_analysis = self._analyze_metrics(figures_of_merit)
        
        # Generate insights using LLM if available
        if self.llm:
            insights = await self._generate_llm_insights(experiment_results, metric_analysis)
        else:
            insights = self._generate_heuristic_insights(experiment_results, metric_analysis)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(metric_analysis, insights)
        
        # Create analysis result
        analysis_result = AnalysisResult(
            experiment_id=experiment_id,
            analysis_type=analysis_type,
            metrics={
                "performance_score": performance_score,
                "metric_quality": metric_analysis["overall_quality"],
                "efficiency_score": self._calculate_efficiency_score(execution_time, figures_of_merit)
            },
            insights=insights,
            recommendations=recommendations,
            confidence=self._calculate_analysis_confidence(metric_analysis),
            timestamp=datetime.now()
        )
        
        # Store for learning
        self.analysis_history.append(analysis_result)
        self.add_to_memory(f"analysis_{experiment_id}", analysis_result.__dict__)
        
        return {
            "analysis_result": analysis_result.__dict__,
            "performance_score": performance_score,
            "key_insights": insights[:3],  # Top 3 insights
            "top_recommendations": recommendations[:3],  # Top 3 recommendations
            "analysis_confidence": analysis_result.confidence
        }
    
    async def _compare_experiments(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Compare multiple experiments."""
        experiments = request.get("experiments", [])
        comparison_criteria = request.get("criteria", ["performance", "efficiency", "novelty"])
        
        logger.info(f"Comparing {len(experiments)} experiments")
        
        if len(experiments) < 2:
            return {"error": "Need at least 2 experiments to compare"}
        
        # Calculate scores for each criterion
        comparison_results = {}
        
        for criterion in comparison_criteria:
            scores = []
            for exp in experiments:
                if criterion == "performance":
                    score = self._calculate_performance_score(
                        exp.get("figures_of_merit", {}),
                        exp.get("execution_time", 0.0),
                        exp.get("success_probability", 0.0)
                    )
                elif criterion == "efficiency":
                    score = self._calculate_efficiency_score(
                        exp.get("execution_time", 0.0),
                        exp.get("figures_of_merit", {})
                    )
                elif criterion == "novelty":
                    score = self._calculate_novelty_score(exp)
                else:
                    score = 0.5  # Default
                
                scores.append(score)
            
            comparison_results[criterion] = {
                "scores": scores,
                "winner_index": np.argmax(scores),
                "score_range": [float(np.min(scores)), float(np.max(scores))],
                "mean_score": float(np.mean(scores))
            }
        
        # Overall ranking
        overall_scores = np.mean([comparison_results[c]["scores"] for c in comparison_criteria], axis=0)
        ranking = np.argsort(overall_scores)[::-1].tolist()  # Descending order
        
        # Generate comparative insights
        comparative_insights = self._generate_comparative_insights(experiments, comparison_results)
        
        return {
            "comparison_results": comparison_results,
            "overall_ranking": ranking,
            "best_experiment_index": int(ranking[0]),
            "comparative_insights": comparative_insights,
            "criteria_weights": {c: 1.0/len(comparison_criteria) for c in comparison_criteria}
        }
    
    async def _extract_insights(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Extract insights from experimental data."""
        data = request.get("data", {})
        insight_types = request.get("types", ["performance", "correlations", "trends"])
        
        logger.info(f"Extracting insights: {insight_types}")
        
        insights = {}
        
        for insight_type in insight_types:
            if insight_type == "performance":
                insights["performance"] = self._extract_performance_insights(data)
            elif insight_type == "correlations":
                insights["correlations"] = self._extract_correlation_insights(data)
            elif insight_type == "trends":
                insights["trends"] = self._extract_trend_insights(data)
            elif insight_type == "anomalies":
                insights["anomalies"] = self._extract_anomaly_insights(data)
        
        # Use LLM for deeper insight generation if available
        if self.llm:
            llm_insights = await self._generate_deep_insights_with_llm(data, insights)
            insights["llm_generated"] = llm_insights
        
        return {
            "insights": insights,
            "insight_confidence": self._calculate_insight_confidence(insights),
            "actionable_items": self._identify_actionable_items(insights)
        }
    
    async def _detect_anomalies(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Detect anomalies in experimental data."""
        data = request.get("data", {})
        baseline_data = request.get("baseline", {})
        sensitivity = request.get("sensitivity", 0.1)
        
        logger.info("Detecting anomalies in experimental data")
        
        anomalies = []
        anomaly_scores = {}
        
        # Statistical anomaly detection
        for metric_name, values in data.items():
            if isinstance(values, (list, np.ndarray)) and len(values) > 1:
                # Z-score based detection
                z_scores = np.abs((values - np.mean(values)) / np.std(values))
                anomaly_indices = np.where(z_scores > 2.0)[0]
                
                if len(anomaly_indices) > 0:
                    anomalies.append({
                        "metric": metric_name,
                        "type": "statistical_outlier",
                        "indices": anomaly_indices.tolist(),
                        "z_scores": z_scores[anomaly_indices].tolist()
                    })
                
                anomaly_scores[metric_name] = float(np.max(z_scores))
        
        # Baseline comparison anomalies
        if baseline_data:
            baseline_anomalies = self._detect_baseline_anomalies(data, baseline_data)
            anomalies.extend(baseline_anomalies)
        
        # Pattern-based anomalies
        pattern_anomalies = self._detect_pattern_anomalies(data)
        anomalies.extend(pattern_anomalies)
        
        return {
            "anomalies": anomalies,
            "anomaly_scores": anomaly_scores,
            "total_anomalies": len(anomalies),
            "severity_assessment": self._assess_anomaly_severity(anomalies)
        }
    
    async def _analyze_patterns(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patterns in experimental data."""
        data = request.get("data", {})
        pattern_types = request.get("pattern_types", ["temporal", "correlational", "cyclical"])
        
        logger.info(f"Analyzing patterns: {pattern_types}")
        
        patterns = {}
        
        for pattern_type in pattern_types:
            if pattern_type == "temporal":
                patterns["temporal"] = self._analyze_temporal_patterns(data)
            elif pattern_type == "correlational":
                patterns["correlational"] = self._analyze_correlation_patterns(data)
            elif pattern_type == "cyclical":
                patterns["cyclical"] = self._analyze_cyclical_patterns(data)
            elif pattern_type == "clustering":
                patterns["clustering"] = self._analyze_clustering_patterns(data)
        
        # Store patterns in database for future reference
        self._update_pattern_database(patterns)
        
        return {
            "patterns": patterns,
            "pattern_strength": self._calculate_pattern_strength(patterns),
            "pattern_significance": self._assess_pattern_significance(patterns)
        }
    
    async def _evaluate_performance(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate overall performance of experiments."""
        experiments = request.get("experiments", [])
        evaluation_criteria = request.get("criteria", {})
        
        logger.info(f"Evaluating performance of {len(experiments)} experiments")
        
        performance_results = []
        
        for exp in experiments:
            performance = {
                "experiment_id": exp.get("experiment_id", "unknown"),
                "scores": {},
                "overall_score": 0.0
            }
            
            # Calculate individual scores
            figures_of_merit = exp.get("figures_of_merit", {})
            for fom_name, fom_value in figures_of_merit.items():
                weight = self.figure_of_merit_weights.get(fom_name, 0.1)
                normalized_score = self._normalize_metric(fom_name, fom_value)
                performance["scores"][fom_name] = normalized_score * weight
            
            # Calculate overall score
            performance["overall_score"] = sum(performance["scores"].values())
            performance_results.append(performance)
        
        # Rank experiments
        sorted_results = sorted(performance_results, 
                               key=lambda x: x["overall_score"], 
                               reverse=True)
        
        return {
            "performance_results": performance_results,
            "ranking": sorted_results,
            "best_experiment": sorted_results[0] if sorted_results else None,
            "performance_distribution": self._analyze_performance_distribution(performance_results)
        }
    
    def _calculate_performance_score(self, figures_of_merit: Dict[str, float],
                                   execution_time: float, success_probability: float) -> float:
        """Calculate composite performance score."""
        score = 0.0
        total_weight = 0.0
        
        # Add FOM contributions
        for fom_name, fom_value in figures_of_merit.items():
            weight = self.figure_of_merit_weights.get(fom_name, 0.1)
            normalized_fom = self._normalize_metric(fom_name, fom_value)
            score += normalized_fom * weight
            total_weight += weight
        
        # Add execution time penalty
        time_penalty = max(0, 1.0 - execution_time / 10.0)  # Penalty after 10 seconds
        score += time_penalty * 0.1
        total_weight += 0.1
        
        # Add success probability contribution
        score += success_probability * 0.2
        total_weight += 0.2
        
        return score / max(total_weight, 1.0)
    
    def _analyze_metrics(self, figures_of_merit: Dict[str, float]) -> Dict[str, Any]:
        """Analyze individual metrics."""
        analysis = {
            "metric_count": len(figures_of_merit),
            "metrics": {},
            "overall_quality": 0.0
        }
        
        quality_scores = []
        
        for metric_name, value in figures_of_merit.items():
            metric_analysis = {
                "value": value,
                "normalized_value": self._normalize_metric(metric_name, value),
                "quality_assessment": self._assess_metric_quality(metric_name, value),
                "benchmark_comparison": self._compare_to_benchmark(metric_name, value)
            }
            
            analysis["metrics"][metric_name] = metric_analysis
            quality_scores.append(metric_analysis["quality_assessment"])
        
        analysis["overall_quality"] = np.mean(quality_scores) if quality_scores else 0.0
        return analysis
    
    async def _generate_llm_insights(self, experiment_results: Dict[str, Any],
                                   metric_analysis: Dict[str, Any]) -> List[str]:
        """Generate insights using LLM."""
        prompt = f"""
Analyze the following quantum experiment results and provide key insights:

EXPERIMENT RESULTS:
- Figures of Merit: {experiment_results.get('figures_of_merit', {})}
- Execution Time: {experiment_results.get('execution_time', 0.0)}s
- Success Probability: {experiment_results.get('success_probability', 0.0)}

METRIC ANALYSIS:
- Overall Quality: {metric_analysis.get('overall_quality', 0.0)}
- Number of Metrics: {metric_analysis.get('metric_count', 0)}

Please provide:
1. Key insights about experiment performance
2. Potential improvements
3. Interesting observations
4. Implications for future experiments

Format as a list of concise insights.
"""
        
        system_prompt = """
You are an expert quantum optics researcher analyzing experimental results. 
Provide clear, actionable insights that would help improve future experiments.
Focus on practical implications and concrete recommendations.
"""
        
        try:
            response = await self.query_llm(prompt, system_prompt)
            # Parse response into list of insights
            insights = [line.strip() for line in response.split('\n') 
                       if line.strip() and not line.strip().startswith('-')]
            return insights[:10]  # Limit to top 10 insights
        except Exception as e:
            logger.error(f"LLM insight generation failed: {e}")
            return self._generate_heuristic_insights(experiment_results, metric_analysis)
    
    def _generate_heuristic_insights(self, experiment_results: Dict[str, Any],
                                   metric_analysis: Dict[str, Any]) -> List[str]:
        """Generate insights using heuristic rules."""
        insights = []
        
        figures_of_merit = experiment_results.get("figures_of_merit", {})
        execution_time = experiment_results.get("execution_time", 0.0)
        success_probability = experiment_results.get("success_probability", 0.0)
        
        # Performance insights
        if metric_analysis.get("overall_quality", 0.0) > 0.8:
            insights.append("Experiment shows excellent overall performance across metrics")
        elif metric_analysis.get("overall_quality", 0.0) < 0.3:
            insights.append("Experiment performance is below expectations - consider redesign")
        
        # Execution time insights
        if execution_time > 5.0:
            insights.append("Long execution time may indicate computational bottlenecks")
        elif execution_time < 0.1:
            insights.append("Very fast execution suggests efficient implementation")
        
        # Success probability insights
        if success_probability > 0.9:
            insights.append("High success probability indicates robust experimental design")
        elif success_probability < 0.5:
            insights.append("Low success probability suggests need for protocol optimization")
        
        # Specific metric insights
        for metric_name, value in figures_of_merit.items():
            if "fidelity" in metric_name.lower() and value > 0.95:
                insights.append(f"Excellent {metric_name} indicates high-quality state preparation")
            elif "entropy" in metric_name.lower() and value < 0.1:
                insights.append(f"Low {metric_name} suggests good quantum coherence")
        
        return insights
    
    def _generate_recommendations(self, metric_analysis: Dict[str, Any], 
                                insights: List[str]) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        overall_quality = metric_analysis.get("overall_quality", 0.0)
        
        if overall_quality < 0.5:
            recommendations.append("Consider fundamental redesign of experimental approach")
            recommendations.append("Investigate sources of noise and decoherence")
        
        # Metric-specific recommendations
        for metric_name, metric_data in metric_analysis.get("metrics", {}).items():
            quality = metric_data.get("quality_assessment", 0.0)
            
            if quality < 0.3:
                if "fidelity" in metric_name.lower():
                    recommendations.append("Improve state preparation fidelity through better control")
                elif "time" in metric_name.lower():
                    recommendations.append("Optimize experimental sequence for faster execution")
                elif "success" in metric_name.lower():
                    recommendations.append("Increase success probability through protocol refinement")
        
        # Insight-based recommendations
        for insight in insights:
            if "bottleneck" in insight.lower():
                recommendations.append("Profile computation to identify and resolve bottlenecks")
            elif "robust" in insight.lower():
                recommendations.append("Explore parameter variations while maintaining robustness")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _calculate_analysis_confidence(self, metric_analysis: Dict[str, Any]) -> float:
        """Calculate confidence in the analysis."""
        # Base confidence on number of metrics and their quality
        metric_count = metric_analysis.get("metric_count", 0)
        overall_quality = metric_analysis.get("overall_quality", 0.0)
        
        # More metrics and higher quality = higher confidence
        confidence = min(1.0, (metric_count / 10.0) * 0.5 + overall_quality * 0.5)
        return confidence
    
    def _calculate_efficiency_score(self, execution_time: float, 
                                  figures_of_merit: Dict[str, float]) -> float:
        """Calculate efficiency score."""
        if execution_time <= 0:
            return 0.0
        
        # Combine performance with speed
        performance = np.mean(list(figures_of_merit.values())) if figures_of_merit else 0.0
        time_efficiency = 1.0 / (1.0 + execution_time)  # Prefer faster execution
        
        return (performance + time_efficiency) / 2.0
    
    def _calculate_novelty_score(self, experiment: Dict[str, Any]) -> float:
        """Calculate novelty score of an experiment."""
        # Compare against historical experiments
        # For now, return a placeholder score
        return 0.5
    
    def _normalize_metric(self, metric_name: str, value: float) -> float:
        """Normalize a metric value to 0-1 range."""
        # Define normalization rules for different metrics
        if "fidelity" in metric_name.lower():
            return max(0.0, min(1.0, value))  # Already 0-1
        elif "entropy" in metric_name.lower():
            return max(0.0, 1.0 - value / 10.0)  # Lower entropy is better
        elif "time" in metric_name.lower():
            return max(0.0, 1.0 - value / 10.0)  # Faster is better
        elif "probability" in metric_name.lower():
            return max(0.0, min(1.0, value))  # Already 0-1
        else:
            # Generic normalization
            return max(0.0, min(1.0, value))
    
    def _assess_metric_quality(self, metric_name: str, value: float) -> float:
        """Assess the quality of a metric value."""
        normalized = self._normalize_metric(metric_name, value)
        
        # Quality thresholds
        if normalized > 0.9:
            return 1.0  # Excellent
        elif normalized > 0.7:
            return 0.8  # Good
        elif normalized > 0.5:
            return 0.6  # Fair
        elif normalized > 0.3:
            return 0.4  # Poor
        else:
            return 0.2  # Very poor
    
    def _compare_to_benchmark(self, metric_name: str, value: float) -> str:
        """Compare metric to benchmark values."""
        normalized = self._normalize_metric(metric_name, value)
        
        if normalized > 0.9:
            return "excellent"
        elif normalized > 0.7:
            return "above_average"
        elif normalized > 0.5:
            return "average"
        elif normalized > 0.3:
            return "below_average"
        else:
            return "poor"
    
    def _generate_comparative_insights(self, experiments: List[Dict[str, Any]],
                                     comparison_results: Dict[str, Any]) -> List[str]:
        """Generate insights from experiment comparison."""
        insights = []
        
        # Find best and worst performers
        for criterion, results in comparison_results.items():
            best_idx = results["winner_index"]
            scores = results["scores"]
            
            best_score = scores[best_idx]
            worst_score = min(scores)
            
            if best_score - worst_score > 0.3:
                insights.append(f"Significant variation in {criterion} performance detected")
            
            if best_score > 0.8:
                insights.append(f"Experiment {best_idx} shows excellent {criterion}")
        
        return insights
    
    def _extract_performance_insights(self, data: Dict[str, Any]) -> List[str]:
        """Extract performance-related insights."""
        insights = []
        
        # Analyze performance trends
        if "performance_history" in data:
            history = data["performance_history"]
            if len(history) > 1:
                trend = np.polyfit(range(len(history)), history, 1)[0]
                if trend > 0.01:
                    insights.append("Performance is improving over time")
                elif trend < -0.01:
                    insights.append("Performance is declining over time")
        
        return insights
    
    def _extract_correlation_insights(self, data: Dict[str, Any]) -> List[str]:
        """Extract correlation insights."""
        insights = []
        
        # Look for correlations between metrics
        numeric_data = {k: v for k, v in data.items() 
                       if isinstance(v, (list, np.ndarray)) and len(v) > 2}
        
        if len(numeric_data) >= 2:
            keys = list(numeric_data.keys())
            for i in range(len(keys)):
                for j in range(i+1, len(keys)):
                    corr = np.corrcoef(numeric_data[keys[i]], numeric_data[keys[j]])[0, 1]
                    if abs(corr) > 0.7:
                        insights.append(f"Strong correlation between {keys[i]} and {keys[j]}")
        
        return insights
    
    def _extract_trend_insights(self, data: Dict[str, Any]) -> List[str]:
        """Extract trend insights."""
        insights = []
        
        # Analyze temporal trends
        for key, values in data.items():
            if isinstance(values, (list, np.ndarray)) and len(values) > 3:
                # Simple linear trend analysis
                x = np.arange(len(values))
                slope = np.polyfit(x, values, 1)[0]
                
                if abs(slope) > 0.01:
                    direction = "increasing" if slope > 0 else "decreasing"
                    insights.append(f"{key} shows {direction} trend")
        
        return insights
    
    def _extract_anomaly_insights(self, data: Dict[str, Any]) -> List[str]:
        """Extract anomaly insights."""
        insights = []
        
        # Simple anomaly detection
        for key, values in data.items():
            if isinstance(values, (list, np.ndarray)) and len(values) > 2:
                mean_val = np.mean(values)
                std_val = np.std(values)
                
                anomalies = [v for v in values if abs(v - mean_val) > 2 * std_val]
                if anomalies:
                    insights.append(f"Detected {len(anomalies)} anomalies in {key}")
        
        return insights
    
    async def _generate_deep_insights_with_llm(self, data: Dict[str, Any],
                                             insights: Dict[str, Any]) -> List[str]:
        """Generate deeper insights using LLM."""
        prompt = f"""
Analyze this experimental data and provide deep insights:

DATA SUMMARY:
{str(data)[:1000]}...

INITIAL INSIGHTS:
{str(insights)[:1000]}...

Provide 3-5 deep, actionable insights that go beyond surface-level observations.
Focus on:
1. Hidden patterns or relationships
2. Implications for experimental design
3. Opportunities for optimization
4. Novel hypotheses for investigation
"""
        
        try:
            response = await self.query_llm(prompt)
            return [line.strip() for line in response.split('\n') 
                   if line.strip() and not line.strip().startswith('-')][:5]
        except Exception as e:
            logger.error(f"Deep insight generation failed: {e}")
            return ["Deep analysis requires LLM integration"]
    
    def _calculate_insight_confidence(self, insights: Dict[str, Any]) -> float:
        """Calculate confidence in extracted insights."""
        # Base confidence on number and variety of insights
        total_insights = sum(len(insight_list) for insight_list in insights.values() 
                           if isinstance(insight_list, list))
        
        confidence = min(1.0, total_insights / 20.0)  # Max confidence at 20 insights
        return confidence
    
    def _identify_actionable_items(self, insights: Dict[str, Any]) -> List[str]:
        """Identify actionable items from insights."""
        actionable = []
        
        for insight_type, insight_list in insights.items():
            if isinstance(insight_list, list):
                for insight in insight_list:
                    if any(word in insight.lower() for word in 
                          ["improve", "optimize", "increase", "reduce", "adjust"]):
                        actionable.append(insight)
        
        return actionable[:5]  # Top 5 actionable items
    
    def _initialize_anomaly_detectors(self) -> Dict[str, Any]:
        """Initialize anomaly detection methods."""
        return {
            "statistical": {"method": "z_score", "threshold": 2.0},
            "isolation_forest": {"contamination": 0.1},
            "local_outlier": {"n_neighbors": 5}
        }
    
    def _detect_baseline_anomalies(self, data: Dict[str, Any], 
                                  baseline: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect anomalies compared to baseline."""
        anomalies = []
        
        for key in data.keys():
            if key in baseline:
                current_val = data[key]
                baseline_val = baseline[key]
                
                if isinstance(current_val, (int, float)) and isinstance(baseline_val, (int, float)):
                    deviation = abs(current_val - baseline_val) / max(abs(baseline_val), 1e-6)
                    
                    if deviation > 0.5:  # 50% deviation threshold
                        anomalies.append({
                            "metric": key,
                            "type": "baseline_deviation",
                            "current_value": current_val,
                            "baseline_value": baseline_val,
                            "deviation_ratio": deviation
                        })
        
        return anomalies
    
    def _detect_pattern_anomalies(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect pattern-based anomalies."""
        # Placeholder for pattern-based anomaly detection
        return []
    
    def _assess_anomaly_severity(self, anomalies: List[Dict[str, Any]]) -> str:
        """Assess overall severity of detected anomalies."""
        if not anomalies:
            return "none"
        elif len(anomalies) <= 2:
            return "low"
        elif len(anomalies) <= 5:
            return "medium"
        else:
            return "high"
    
    def _analyze_temporal_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze temporal patterns in data."""
        patterns = {}
        
        for key, values in data.items():
            if isinstance(values, (list, np.ndarray)) and len(values) > 3:
                # Simple trend analysis
                x = np.arange(len(values))
                slope, intercept = np.polyfit(x, values, 1)
                
                patterns[key] = {
                    "trend_slope": float(slope),
                    "trend_intercept": float(intercept),
                    "trend_strength": float(abs(slope) / (np.std(values) + 1e-6))
                }
        
        return patterns
    
    def _analyze_correlation_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze correlation patterns."""
        patterns = {}
        
        numeric_data = {k: v for k, v in data.items() 
                       if isinstance(v, (list, np.ndarray)) and len(v) > 2}
        
        if len(numeric_data) >= 2:
            keys = list(numeric_data.keys())
            correlations = {}
            
            for i in range(len(keys)):
                for j in range(i+1, len(keys)):
                    try:
                        corr = np.corrcoef(numeric_data[keys[i]], numeric_data[keys[j]])[0, 1]
                        if not np.isnan(corr):
                            correlations[f"{keys[i]}_vs_{keys[j]}"] = float(corr)
                    except:
                        pass
            
            patterns["correlations"] = correlations
        
        return patterns
    
    def _analyze_cyclical_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cyclical patterns."""
        # Placeholder for cyclical pattern analysis
        return {"cyclical_detected": False}
    
    def _analyze_clustering_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze clustering patterns."""
        # Placeholder for clustering analysis
        return {"clusters_detected": 0}
    
    def _update_pattern_database(self, patterns: Dict[str, Any]):
        """Update the pattern database with new findings."""
        timestamp = datetime.now().isoformat()
        self.pattern_database[timestamp] = patterns
        
        # Keep only recent patterns (last 100)
        if len(self.pattern_database) > 100:
            oldest_key = min(self.pattern_database.keys())
            del self.pattern_database[oldest_key]
    
    def _calculate_pattern_strength(self, patterns: Dict[str, Any]) -> float:
        """Calculate overall strength of detected patterns."""
        strengths = []
        
        for pattern_type, pattern_data in patterns.items():
            if isinstance(pattern_data, dict):
                # Extract numeric strength indicators
                for key, value in pattern_data.items():
                    if isinstance(value, (int, float)) and "strength" in key.lower():
                        strengths.append(abs(value))
        
        return float(np.mean(strengths)) if strengths else 0.0
    
    def _assess_pattern_significance(self, patterns: Dict[str, Any]) -> str:
        """Assess significance of detected patterns."""
        strength = self._calculate_pattern_strength(patterns)
        
        if strength > 0.8:
            return "high"
        elif strength > 0.5:
            return "medium"
        elif strength > 0.2:
            return "low"
        else:
            return "negligible"
    
    def _analyze_performance_distribution(self, performance_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze distribution of performance scores."""
        scores = [result["overall_score"] for result in performance_results]
        
        return {
            "mean_score": float(np.mean(scores)),
            "std_score": float(np.std(scores)),
            "min_score": float(np.min(scores)),
            "max_score": float(np.max(scores)),
            "score_range": float(np.max(scores) - np.min(scores))
        }
