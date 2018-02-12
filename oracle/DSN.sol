pragma solidity ^0.4.4;
contract CrowdBank {
    
    address public oracle;

    Provider[] public providerList;

    mapping (address=>uint) public providerMap;
    mapping (address=>Service) public serviceMap;

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
    }

    function CrowdBank() public {
        oracle = msg.sender;
    }

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

    function getSToken(address provider) public constant returns(uint){
        if(providerMap[provider] == 0) return 0;
        return providerList[providerMap[provider]].sToken;
    }

    // Sent by provider
    // Allowing only 1 service by a provider
    function useService(uint numToken, uint rate, address client) public {
        if(providerMap[msg.sender] == 0) return;
        if(providerList[providerMap[msg.sender]].sToken < numToken) return;

        // Subtract used tokens from issued Tokens
        uint pos = providerMap[msg.sender];
        providerList[pos].sToken = providerList[pos].sToken - numToken;

        // Add Service
        serviceMap[msg.sender] = Service(msg.sender, client, numToken, rate);
    }  

    // Sent by client
    function revokeService(address provider) public {
        if(providerMap[provider] == 0) return;
        if(serviceMap[provider].provider == 0) return;
        if(serviceMap[provider].client != msg.sender) return;
        uint tokenUsed = serviceMap[provider].numToken;

        // Return sToken
        uint pos = providerMap[provider];
        providerList[pos].sToken = providerList[pos].sToken + tokenUsed;

        // Remove service
        serviceMap[provider].provider = 0;
    }
}