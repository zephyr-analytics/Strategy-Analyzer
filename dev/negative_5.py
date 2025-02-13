def run_backtest(self):
    """
    Runs the backtest by calculating portfolio values and returns over time.
    If the benchmark drops -5% in a single day, move equities to cash for the rest of the month.
    """
    monthly_dates = self._prepare_date_ranges()
    step = self._determine_step_size()

    portfolio_values = [int(self.data_models.initial_portfolio_value)]
    portfolio_values_without_contributions = [int(self.data_models.initial_portfolio_value)]
    portfolio_returns = []
    tax_adjusted_values = [int(self.data_models.initial_portfolio_value)]
    all_adjusted_weights = []

    for i in range(0, len(monthly_dates), step):
        current_date = monthly_dates[i]
        last_date_current_month = self._get_last_trading_date(current_date)

        # Get benchmark drop information
        drop_day, cumulative_return_before_drop, in_cash = self._adjust_for_benchmark_drop(last_date_current_month)

        # Get normal asset allocation unless in cash
        adjusted_weights = {"CASH": 1.0} if in_cash else self.get_portfolio_assets_and_weights(current_date=last_date_current_month)

        for j in range(step):
            if i + j >= len(monthly_dates) - 1:
                break

            next_date = monthly_dates[i + j + 1]
            last_date_next_month = self._get_last_trading_date(next_date)

            if drop_day and next_date > drop_day:
                # After the drop: 0% return (portfolio is in cash)
                month_return = 0.0  
                adjusted_weights = {"CASH": 1.0}  # Move portfolio fully to cash
            else:
                # Before the drop or if no drop occurs: Normal return calculation
                month_return = self._calculate_monthly_return(last_date_current_month, last_date_next_month, adjusted_weights)

            portfolio_returns.append(month_return)

            new_portfolio_value, new_portfolio_value_without_contributions = self._calculate_new_portfolio_values(
                portfolio_values[-1], portfolio_values_without_contributions[-1], month_return, self.data_models.contribution
            )

            portfolio_values.append(new_portfolio_value)
            portfolio_values_without_contributions.append(new_portfolio_value_without_contributions)

            if self.data_models.use_tax == "True":
                new_tax_adjusted_value = self._calculate_tax_adjusted_value(
                    tax_adjusted_values[-1], portfolio_values[-2], portfolio_values[-1], self.data_models.tax_rate, month_return
                )
                tax_adjusted_values.append(new_tax_adjusted_value)

            all_adjusted_weights.append(adjusted_weights)
            last_date_current_month = last_date_next_month

    return {
        "all_adjusted_weights": all_adjusted_weights,
        "portfolio_values": portfolio_values,
        "portfolio_values_without_contributions": portfolio_values_without_contributions,
        "portfolio_returns": portfolio_returns,
        "tax_adjusted_values": tax_adjusted_values
    }

def _adjust_for_benchmark_drop(self, last_date_current_month):
    """
    Checks if the benchmark fell -5% in a single day within the month.
    Returns:
    - drop_day: The exact day the benchmark dropped (-5%) or None.
    - cumulative_return_before_drop: The return accumulated before the drop.
    - in_cash: Whether the portfolio should be in cash mode.
    """
    daily_benchmark_returns = self._get_daily_returns(self.data_models.benchmark_asset, last_date_current_month)

    drop_day = None
    cumulative_return_before_drop = 1.0

    for date, daily_return in daily_benchmark_returns.items():
        if daily_return <= -0.05:
            drop_day = date
            break
        cumulative_return_before_drop *= (1 + daily_return)  # Accumulate return before drop

    in_cash = drop_day is not None  # If a drop occurred, portfolio moves to cash

    return drop_day, cumulative_return_before_drop, in_cash

