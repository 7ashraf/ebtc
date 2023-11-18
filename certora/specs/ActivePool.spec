import "./sanity.spec";
import "./erc20.spec";

using CollateralTokenTester as collateral;
using DummyERC20A as erc;
using CdpManager as cdp;
//using CollSurplusPoolHarness as pool;
methods {
    function _.increaseTotalSurplusCollShares(uint256) external => DISPATCHER(true);
    function _.onFlashLoan(address, address, uint256, uint256, bytes) external => DISPATCHER(true);
    function _.getSystemCollShares() external => DISPATCHER(true);
    function _.transferSystemCollShares(address, uint256) external => DISPATCHER(true);
    function transferSystemCollSharesAndLiquidatorReward(
        address _account,
        uint256 _shares,
        uint256 _liquidatorRewardShares
    ) external;
    function sharesOf(address _account) external returns (uint256);
    function getSystemCollShares() external   returns (uint256);
    function increaseSystemDebt(uint256 _amount) external;
    function decreaseSystemDebt(uint256 _amount) external;
    function getSystemDebt() external returns (uint256);
    function allocateSystemCollSharesToFeeRecipient(uint256 _shares) external;
    function ActivePool.getFeeRecipientClaimableCollShares() external  returns (uint256);
    function increaseSystemCollShares(uint256 _value) external;
    function claimFeeRecipientCollShares(uint256 _shares) external;
    //function getFeeRecpNew() external returns(address);
    function sweepToken(address token, uint256 amount) external;
    function erc.balanceOf(address account) external  returns (uint256);
    function erc.myAddress() external returns (address);
    function cdp.syncGlobalAccountingAndGracePeriod() external;

}


use rule sanity;


rule transferSystemCollSharesSpec(env e){
    address account;
    uint256 shares;

    mathint systemCollSharesBefore = getSystemCollShares(e);



    require shares > 0;

    transferSystemCollShares(e, account, shares);

    mathint systemCollSharesAfter = getSystemCollShares(e);

    //assert system coll shares = before - shares
    assert systemCollSharesAfter == (systemCollSharesBefore - shares);

    //assert the function called works correctly within the function
}

rule transferSystemCollSharesAndLiquidatorRewardSpec(env e, address user, uint256 shares, uint256 liquidatorRewardShares){
    require shares >0;
    require user != currentContract;
    //states changed:
    //systemCollShares
    //sharesOf(account)
    //states not changed (other accounts)
    mathint totalShares = shares + liquidatorRewardShares;

    mathint systemCollSharesBefore = getSystemCollShares(e);
    mathint userSharesBefore = collateral.sharesOf(e, user);


    transferSystemCollSharesAndLiquidatorReward(e, user, shares, liquidatorRewardShares);

    mathint systemCollSharesAfter = getSystemCollShares(e);
    mathint userSharesAfter = collateral.sharesOf(e, user);


    assert systemCollSharesAfter == systemCollSharesBefore - shares;
    assert userSharesAfter == userSharesBefore + totalShares;
    //assert user == collSurplusPoolAddress => totalSharesAfter == totalSharesBefore + totalShares;


}

rule allocateSystemCollSharesToFeeRecipientSpec(env e, uint256 shares){
    require shares >0;
    
    mathint systemCollSharesBefore = getSystemCollShares(e);
    mathint feeRecipientCollSharesBefore = getFeeRecipientClaimableCollShares(e);

    allocateSystemCollSharesToFeeRecipient(e, shares);

    mathint systemCollSharesAfter = getSystemCollShares(e);
    mathint feeRecipientCollSharesAfter = getFeeRecipientClaimableCollShares(e);

    assert systemCollSharesAfter == systemCollSharesBefore - shares;
    assert feeRecipientCollSharesAfter == feeRecipientCollSharesBefore + shares;

}

rule increaseSystemDebtSpec(env e, uint256 amount){
    mathint systemDebtBefore = getSystemDebt(e);

    increaseSystemDebt(e, amount);

    mathint systemDebtAfter = getSystemDebt(e);

    assert systemDebtAfter == systemDebtBefore + amount;
}

rule decreaseSystemDebtSpec(env e, uint256 amount){
    mathint systemDebtBefore = getSystemDebt(e);

    decreaseSystemDebt(e, amount);

    mathint systemDebtAfter = getSystemDebt(e);

    assert systemDebtAfter == systemDebtBefore - amount;
}

rule increaseSystemCollSharesSpec(env e, uint256 value){
    require value >0;

    mathint systemCollSharesBefore = getSystemCollShares(e);

    increaseSystemCollShares(e, value);

    mathint systemCollSharesAfter = getSystemCollShares(e);

    assert systemCollSharesAfter == systemCollSharesBefore + value;
}
rule claimFeeRecipientCollSharesSpec(env e, uint256 shares){
    address account;
    require shares > 0;
    
    address feeRecipientAdress = currentContract.feeRecipientAddress;
    require feeRecipientAdress != currentContract;
    require account != currentContract && account != feeRecipientAdress;
    require e.msg.sender != currentContract;

    //function changes the contract states before saving them
    cdp.syncGlobalAccountingAndGracePeriod(e);

    mathint feeRecipientCollSharesBefore = getFeeRecipientClaimableCollShares(e);
    require assert_uint256(feeRecipientCollSharesBefore) >= shares;
    mathint feeRecipientCollBalanceBefore = collateral.sharesOf(e, feeRecipientAdress);
    mathint contractBalanceBefore = collateral.sharesOf(e, currentContract);
    mathint accountBalanceBefore = collateral.sharesOf(e, account);
    mathint systemCollSharesBefore = getSystemCollShares(e);

    claimFeeRecipientCollShares(e, shares);

    mathint feeRecipientCollSharesAfter = getFeeRecipientClaimableCollShares(e);
    mathint feeRecipientCollBalanceAfter = collateral.sharesOf(e, feeRecipientAdress);
    mathint contractBalanceAfter = collateral.sharesOf(e, currentContract);
    mathint systemCollSharesAfter = getSystemCollShares(e);

    mathint accountBalanceAfter = collateral.sharesOf(e, account);

    assert feeRecipientCollSharesAfter == feeRecipientCollSharesBefore - shares;
    assert feeRecipientCollBalanceAfter == feeRecipientCollBalanceBefore + shares;
    assert contractBalanceAfter == contractBalanceBefore - shares;
    //assert systemCollSharesAfter == systemCollSharesBefore - shares;

    assert accountBalanceAfter == accountBalanceBefore;
}

rule sweepToken(env e, address token, uint256 amount){
    require amount > 0;
    address account;
    address feeRecipientAddress = currentContract.feeRecipientAddress;
    require account != currentContract && account != feeRecipientAddress && account != token;
    require token == erc.myAddress(e);
    require feeRecipientAddress != currentContract;


    

    mathint contractBalanceBefore = erc.balanceOf(e, currentContract);
    mathint recipientBalanceBefore = erc.balanceOf(e, feeRecipientAddress);
    mathint accountBalanceBefore = erc.balanceOf(e, account);

    sweepToken(e, token, amount);

    mathint contractBalanceAfter = erc.balanceOf(e, currentContract);
    mathint recipientBalanceAfter = erc.balanceOf(e, feeRecipientAddress);
    mathint accountBalanceAfter = erc.balanceOf(e, account);

    assert contractBalanceAfter == contractBalanceBefore - amount;
    assert recipientBalanceAfter == recipientBalanceBefore + amount;
    
    assert accountBalanceAfter == accountBalanceBefore;

}

