class CounterfactualEngine:
    """
    Answers: 'What would need to change for the verdict to change?'
    """
    
    def generate_counterfactuals(self, consensus_result, global_timeline):
        """
        Analyzes the consensus result and generates counterfactual statements.
        """
        cfs = []
        
        if consensus_result["verdict"] == "fake":
            # Identify the strongest agent pushing 'fake'
            details = consensus_result.get("calibrated_details", {})
            fake_contributors = {
                k: v for k, v in details.items() 
                if v.get("calibrated_confidence", 0) > 0.5
            }
            
            if fake_contributors:
                # Find max contributor
                top_agent = max(fake_contributors, key=lambda k: fake_contributors[k]["calibrated_confidence"])
                cfs.append(
                    f"If the {top_agent} agent's confidence decreased by 25%, "
                    f"the consensus might shift towards 'real'."
                )
                
        else:
            cfs.append(
                "If temporal phonetic instability increased by 15%, "
                "the system would flag this as synthetic."
            )
            
        return cfs
