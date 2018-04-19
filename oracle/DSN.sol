pragma solidity ^0.4.4;
contract CrowdBank {
    
    address public oracle;

    Provider[] public providerList;
    Service[] public servList;

    mapping (address=>uint) public providerMap;
    mapping (address=>uint[]) public serviceMap;

    struct Provider {
        address provider;
        uint sToken;
        bytes32 ip;
    }

    struct Service {
        address provider;
        address client;
        uint numToken;
        uint rate;
        uint eTime;
        uint lVTime;
    }

    function CrowdBank() public {
        oracle = msg.sender;
        providerList.push(Provider(0, 0, 0));
    }

    // called by oracle
    function issueToken(address provider, uint tokenSize, bytes32 ip) public {
        if(msg.sender != oracle) return;
        if(providerMap[provider] == 0) {
            providerList.push(Provider(provider, tokenSize, ip));
            providerMap[provider] = providerList.length-1;
        }
        else {
            uint pos = providerMap[provider];
            providerList[pos].sToken = tokenSize;
            providerList[pos].ip = ip;
        }
    }

    function getProvider(uint pos) public constant returns(address, uint, bytes32) {
    	if(pos >= providerList.length) return (0,0,0);
    	Provider obj = providerList[pos];
    	return (obj.provider, obj.sToken, obj.ip);
    }

    function getSToken(address provider) public constant returns(uint) {
        if(providerMap[provider] == 0) return 0;
        return providerList[providerMap[provider]].sToken;
    }

    // Sent by provider
    // Allowing only 1 service by a provider
    function createService(uint numToken, uint rate, address client) public {
        if(providerMap[msg.sender] == 0) return;
        if(providerList[providerMap[msg.sender]].sToken < numToken) return;

        // Subtract used tokens from issued Tokens
        uint pos = providerMap[msg.sender];
        providerList[pos].sToken = providerList[pos].sToken - numToken;

        // Add Service
        uint eTime = block.timestamp;
        uint lVTime = block.timestamp;
        servList.push(Service(msg.sender, client, numToken, rate, eTime, lVTime));
        serviceMap[msg.sender].push(servList.length-1);
    }  

    // Sent by client 
    // Assuming 1 day of service extension
    function payService(address provider, uint pos) payable {
        if(providerMap[provider] == 0) return;
        if(serviceMap[provider][pos].provider != provider) return;
        uint amount = msg.value;
        if(amount < serviceMap[provider][pos].rate) {
            msg.sender.send(amount);
            return;
        }

        if(serviceMap[provider][pos].lVTime == serviceMap[provider][pos].eTime) { 
            // Service not yet initiated
            // Add money in buffer 
            // Do nothing
        }
        else {
            provider.send(serviceMap[provider][pos].rate);
        }
        uint lVTime = block.timestamp;
        serviceMap[provider][pos].lVTime = lVTime;
        serviceMap[provider][pos].eTime = lVTime + (24*60*60);
    }

    // Sent by provider
    function revokeService(uint spos) public {
        address provider = msg.sender;
        if(providerMap[provider] == 0) return;
        if(serviceMap[provider][spos].provider != msg.sender) return;
        if(serviceMap[provider][spos].eTime > block.timestamp) return;

        uint tokenUsed = serviceMap[provider][spos].numToken;

        // Return sToken
        uint ppos = providerMap[provider];
        providerList[ppos].sToken = providerList[ppos].sToken + tokenUsed;

        // Remove service
        serviceMap[provider][spos].provider = 0;
    }
}