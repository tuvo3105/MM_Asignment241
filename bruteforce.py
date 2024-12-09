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
        Implements a brute force policy to minimize trim loss.
        """
        print(f"Running brute force Policy2210xxx with ID: {self.policy_id}")

        # Initialize the best placement
        best_placement = None
        min_trim_loss = float("inf")  # Minimum trim loss found

        for prod in observation["products"]:
            if prod["quantity"] > 0:  # Only consider products with positive quantity
                prod_size = prod["size"]

                # Evaluate all possible placements across all stocks
                for stock_idx, stock in enumerate(observation["stocks"]):
                    stock_w, stock_h = self._get_stock_size_(stock)

                    # Try both orientations of the product
                    for orientation in [(prod_size[0], prod_size[1]), (prod_size[1], prod_size[0])]:
                        prod_w, prod_h = orientation
                        if stock_w >= prod_w and stock_h >= prod_h:
                            # Check every valid position on the stock
                            for x in range(stock_w - prod_w + 1):
                                for y in range(stock_h - prod_h + 1):
                                    if self._can_place_(stock, (x, y), (prod_w, prod_h)):
                                        # Calculate trim loss if placed here
                                        remaining_w = stock_w - (x + prod_w)
                                        remaining_h = stock_h - (y + prod_h)
                                        trim_loss = remaining_w * stock_h + remaining_h * stock_w - remaining_w * remaining_h

                                        # Update the best placement if this is optimal
                                        if trim_loss < min_trim_loss:
                                            min_trim_loss = trim_loss
                                            best_placement = {
                                                "stock_idx": stock_idx,
                                                "size": [prod_w, prod_h],
                                                "position": (x, y),
                                            }

        # Return the best placement found
        if best_placement:
            return best_placement

        # If no valid placement is found, return an invalid action
        return {"stock_idx": -1, "size": [0, 0], "position": (0, 0)}
        pass

    # Student code here
    # You can add more functions if needed