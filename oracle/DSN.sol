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

    function getProviderByAddress(address provider) public constant returns(uint, uint) {
        if(providerMap[provider] == 0) return (0,0);
        return (providerMap[provider],providerList[providerMap[provider]].sToken);
    }

    function getProviderServiceCount(address provider) public constant returns(uint) {
        return serviceMap[provider].length;
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
        uint servNo = serviceMap[provider][pos];
        if(servList[servNo].provider != provider) return;
        uint amount = msg.value;
        if(amount < servList[servNo].rate) {
            msg.sender.send(amount);
            return;
        }

        if(servList[servNo].lVTime == servList[servNo].eTime) { 
            // Service not yet initiated
            // Add money in buffer 
            // Do nothing
        }
        else {
            provider.send(servList[servNo].rate);
        }
        uint lVTime = block.timestamp;
        servList[servNo].lVTime = lVTime;
        servList[servNo].eTime = lVTime + (24*60*60);
    }

    // Sent by provider
    function revokeService(uint spos) public {
        address provider = msg.sender;
        if(providerMap[provider] == 0) return;
        uint servNo = serviceMap[provider][spos];
        if(servList[servNo].provider != msg.sender) return;
        if(servList[servNo].eTime > block.timestamp) return;

        uint tokenUsed = servList[servNo].numToken;

        // Return sToken
        uint ppos = providerMap[provider];
        providerList[ppos].sToken = providerList[ppos].sToken + tokenUsed;

        // Remove service
        servList[servNo].provider = 0;
        servList[servNo].client = 0;
    }
}