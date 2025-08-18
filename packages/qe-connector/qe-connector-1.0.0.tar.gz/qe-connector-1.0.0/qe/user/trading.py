from qe.lib.utils import check_required_parameters


def get_master_orders(self, **kwargs):
    """Get master orders (USER_DATA)
    
    Query master orders list
    
    GET /user/trading/master-orders
    
    Keyword Args:
        page (int, optional): Page number
        pageSize (int, optional): Page size
        status (str, optional): Order status filter
        exchange (str, optional): Exchange name filter
        symbol (str, optional): Trading symbol filter
        startTime (str, optional): Start time filter
        endTime (str, optional): End time filter
        recvWindow (int, optional): The value cannot be greater than 60000
    """
    url_path = "/user/trading/master-orders"
    return self.sign_request("GET", url_path, {**kwargs})


def get_order_fills(self, **kwargs):
    """Get order fills (USER_DATA)
    
    Query order fills/trades list
    
    GET /user/trading/order-fills
    
    Keyword Args:
        page (int, optional): Page number
        pageSize (int, optional): Page size
        masterOrderId (str, optional): Master order ID filter
        subOrderId (str, optional): Sub order ID filter
        symbol (str, optional): Trading symbol filter
        startTime (str, optional): Start time filter
        endTime (str, optional): End time filter
        recvWindow (int, optional): The value cannot be greater than 60000
    """
    url_path = "/user/trading/order-fills"
    return self.sign_request("GET", url_path, {**kwargs})


def create_master_order(self, algorithm: str, algorithmType: str, exchange: str, 
                       symbol: str, marketType: str, side: str, apiKeyId: str, **kwargs):
    """Create master order (USER_DATA)
    
    Create a new master order
    
    POST /user/trading/master-orders
    
    Args:
        algorithm (str): Algorithm name
        algorithmType (str): Algorithm type
        exchange (str): Exchange name
        symbol (str): Trading symbol
        marketType (str): Market type
        side (str): Order side (BUY/SELL)
        apiKeyId (str): API key ID to use
    Keyword Args:
        totalQuantity (float, optional): Total quantity to trade
        orderNotional (float, optional): Order notional value
        strategyType (str, optional): Strategy type
        startTime (str, optional): Start time
        executionDuration (str, optional): Execution duration
        endTime (str, optional): End time
        limitPrice (float, optional): Limit price
        mustComplete (bool, optional): Must complete flag
        makerRateLimit (float, optional): Maker rate limit
        povLimit (float, optional): POV limit
        marginType (str, optional): Margin type
        reduceOnly (bool, optional): Reduce only flag
        notes (str, optional): Order notes
        clientId (str, optional): Client order ID
        worstPrice (float, optional): Worst acceptable price
        limitPriceString (str, optional): Limit price as string
        upTolerance (str, optional): Up tolerance
        lowTolerance (str, optional): Low tolerance
        strictUpBound (bool, optional): Strict upper bound flag
        recvWindow (int, optional): The value cannot be greater than 60000
    """
    check_required_parameters([
        [algorithm, "algorithm"],
        [algorithmType, "algorithmType"],
        [exchange, "exchange"],
        [symbol, "symbol"],
        [marketType, "marketType"],
        [side, "side"],
        [apiKeyId, "apiKeyId"]
    ])
    
    params = {
        "algorithm": algorithm,
        "algorithmType": algorithmType,
        "exchange": exchange,
        "symbol": symbol,
        "marketType": marketType,
        "side": side,
        "apiKeyId": apiKeyId,
        **kwargs
    }
    url_path = "/user/trading/master-orders"
    return self.sign_request("POST", url_path, params)


def cancel_master_order(self, masterOrderId: str, **kwargs):
    """Cancel master order (USER_DATA)
    
    Cancel an existing master order
    
    PUT /user/trading/master-orders/{masterOrderId}/cancel
    
    Args:
        masterOrderId (str): Master order ID to cancel
    Keyword Args:
        reason (str, optional): Cancellation reason
        recvWindow (int, optional): The value cannot be greater than 60000
    """
    check_required_parameters([[masterOrderId, "masterOrderId"]])
    
    params = {"masterOrderId": masterOrderId, **kwargs}
    url_path = f"/user/trading/master-orders/{masterOrderId}/cancel"
    return self.sign_request("PUT", url_path, params)
