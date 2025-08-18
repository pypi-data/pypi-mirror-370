from typing import Optional

class CVSSCalculator:
    """
    Utility for calculating CVSS v3.1 scores based on vulnerability characteristics.
    Extensible for custom scoring logic and integration with reporting.
    """
    @staticmethod
    def calculate_cvss_score(
        attack_vector: str = "Network",
        attack_complexity: str = "Low",
        privileges_required: str = "None",
        user_interaction: str = "None",
        scope: str = "Unchanged",
        confidentiality: str = "High",
        integrity: str = "High",
        availability: str = "High",
        exploit_success: bool = True,
        authentication_required: bool = False,
        data_impact: str = "High"
    ) -> float:
        """
        Calculate a CVSS v3.1 score based on vulnerability characteristics.
        :param attack_vector: Network, Adjacent, Local, or Physical
        :param attack_complexity: Low or High
        :param privileges_required: None, Low, or High
        :param user_interaction: None or Required
        :param scope: Unchanged or Changed
        :param confidentiality: High, Medium, or Low
        :param integrity: High, Medium, or Low
        :param availability: High, Medium, or Low
        :param exploit_success: Whether the exploit was successful
        :param authentication_required: Whether authentication is required
        :param data_impact: High, Medium, or Low
        :return: CVSS score (float, 0-10)
        """
        # Simple mapping for demo; replace with full CVSS logic as needed
        base_score = 0.0
        vector_weights = {
            "Network": 1.0, "Adjacent": 0.85, "Local": 0.62, "Physical": 0.2,
            "Low": 0.77, "High": 0.44,
            "None": 0.85, "Required": 0.62,
            "Unchanged": 1.0, "Changed": 1.2,
            "High": 0.56, "Medium": 0.22, "Low": 0.0
        }
        base_score += vector_weights.get(attack_vector, 1.0)
        base_score += vector_weights.get(attack_complexity, 0.77)
        base_score += vector_weights.get(privileges_required, 0.85)
        base_score += vector_weights.get(user_interaction, 0.85)
        base_score += vector_weights.get(scope, 1.0)
        base_score += vector_weights.get(confidentiality, 0.56)
        base_score += vector_weights.get(integrity, 0.56)
        base_score += vector_weights.get(availability, 0.56)
        if not exploit_success:
            base_score *= 0.7
        if authentication_required:
            base_score *= 0.8
        if data_impact == "High":
            base_score += 1.0
        elif data_impact == "Medium":
            base_score += 0.5
        elif data_impact == "Low":
            base_score += 0.1
        return min(round(base_score, 1), 10.0) 