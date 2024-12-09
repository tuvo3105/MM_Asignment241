from policy import Policy


class Policy2210xxx(Policy):
    def __init__(self, policy_id=1):
        """
        Initializes the custom policy with a specific ID.
        """
        assert policy_id in [1, 2], "Policy ID must be 1 or 2"
        self.policy_id = policy_id  # Store the policy ID for later use

        # Student code here
        if policy_id == 1:
            pass
        elif policy_id == 2:
            pass

    def get_action(self, observation, info):
        """
        Implements an optimized greedy policy to minimize trim loss.
        """
        print(f"Running optimized Policy2210xxx with ID: {self.policy_id}")

        # Sort products by descending area
        list_prods = sorted(
            observation["products"],
            key=lambda prod: prod["size"][0] * prod["size"][1],
            reverse=True,
        )

        for prod in list_prods:
            if prod["quantity"] > 0:  # Only consider products with positive quantity
                prod_size = prod["size"]

                # Try to place the product in the best-fit stock
                best_placement = None
                min_waste = float("inf")  # Initialize the minimum waste

                for stock_idx, stock in enumerate(observation["stocks"]):
                    stock_w, stock_h = self._get_stock_size_(stock)

                    for orientation in [(prod_size[0], prod_size[1]), (prod_size[1], prod_size[0])]:
                        prod_w, prod_h = orientation
                        if stock_w >= prod_w and stock_h >= prod_h:
                            for x in range(stock_w - prod_w + 1):
                                for y in range(stock_h - prod_h + 1):
                                    if self._can_place_(stock, (x, y), (prod_w, prod_h)):
                                        # Calculate the waste if placed here
                                        remaining_w = stock_w - (x + prod_w)
                                        remaining_h = stock_h - (y + prod_h)
                                        waste = remaining_w * remaining_h

                                        # Update the best placement if this is more optimal
                                        if waste < min_waste:
                                            min_waste = waste
                                            best_placement = {
                                                "stock_idx": stock_idx,
                                                "size": [prod_w, prod_h],
                                                "position": (x, y),
                                            }

                if best_placement:
                    return best_placement

        # If no valid placement is found, return an invalid action
        return {"stock_idx": -1, "size": [0, 0], "position": (0, 0)}
        pass

    # Student code here
    # You can add more functions if needed