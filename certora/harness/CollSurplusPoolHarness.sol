// SPDX-License-Identifier: MIT

pragma solidity 0.8.17;

import "../../packages/contracts/contracts/CollSurplusPool.sol";

contract CollSurplusPoolHarness is CollSurplusPool { 
    
    constructor(
        address _borrowerOperationsAddress,
        address _cdpManagerAddress,
        address _activePoolAddress,
        address _collTokenAddress
    ) CollSurplusPool(_borrowerOperationsAddress, _cdpManagerAddress, _activePoolAddress, _collTokenAddress) {

    }

    
    function call_isAuthorized(address user, uint32 functionSig) external view returns (bool) {
        return isAuthorized(user, bytes4(functionSig));
    }

    function getContractBalance(address token) external returns (uint256){
        uint256 balance = IERC20(token).balanceOf(address(this));
        return balance;
    }

    function getFeeRecp() external returns(address){
        return IActivePool(activePoolAddress).feeRecipientAddress();
    }

    function getFeeRecpNew() external returns(address){
        return feeRecipientAddress;
    }
}
