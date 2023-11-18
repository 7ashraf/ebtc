import "./sanity.spec";
import "./erc20.spec";


using CollateralTokenTester as collateral;
using DummyERC20A as erc20;
 
methods {
    
    function call_isAuthorized(address user, uint32 functionSig) external  returns (bool) envfree;
    function borrowerOperationsAddress() external  returns (address) envfree;
    //function _.balanceOf(address)                    external  => DISPATCHER(true);
    function getContractBalance(address) external returns (uint256) envfree;
    function balanceOf(address) external  returns (uint256);
    function myAddress() external returns (address);
    // collateral methods
    function collateral.balanceOf(address) external returns (uint256) envfree;
    function collateral.sharesOf(address) external returns (uint256) envfree;
    function getFeeRecp() external returns(address);
    function getFeeRecpNew() external returns(address);
    function increaseSurplusCollShares(address _account, uint256 _amount) external;
    function getSurplusCollShares(address _account) external returns (uint256) envfree;
    function claimSurplusCollShares(address _account) external;
    function getTotalSurplusCollShares() external returns (uint256) ;
    function increaseTotalSurplusCollShares(uint256 _value) external;
    function sharesOf(address _account) external returns (uint256);

}



rule reachability(method f) {
    env e;
    calldataarg args;
    f(e,args);
    satisfy true;
}


rule changeToCollateralBalance(method f) {
    uint256 before = collateral.balanceOf(currentContract);
    env e;
    calldataarg args;
    f(e,args);
    uint256 after = collateral.balanceOf(currentContract);
    assert after < before =>  
        ( call_isAuthorized(e.msg.sender, f.selector) || e.msg.sender == borrowerOperationsAddress()); 
}


rule sweepTokenSpec(env e){
    uint256 amount;
    address accounts;


    address user = getFeeRecpNew(e);
    address token = erc20.myAddress(e);
    mathint contractBalanceBefore = erc20.balanceOf(e, currentContract);
    mathint userBalanceBefore = erc20.balanceOf(e, user);
    mathint accountsBalanceBefore = erc20.balanceOf(e, accounts);
    

    require amount > 0;
    require currentContract != user;
    require e.msg.sender == accounts;
    require currentContract != accounts;
    
    sweepToken(e, token, amount);


    mathint contractBalanceAfter = erc20.balanceOf(e, currentContract);
    mathint userBalanceAfter = erc20.balanceOf(e, user);
    mathint accountsBalanceAfter = erc20.balanceOf(e, accounts);


    //assert the correct state changes 
    assert userBalanceAfter == (userBalanceBefore + amount);
    assert contractBalanceAfter == (contractBalanceBefore - amount);

    //assert the invariant did not change which will make the msg.sender balance did not change 
    //assert invariantBefore == invariantAfter;
    //assert all other balances did not change 
    require user != accounts;
    assert accountsBalanceBefore == accountsBalanceAfter;
    


}

rule increaseSurplusCollSharesSpec(env e){

    address user;
    address account;
    uint256 amount;
    require amount >0;
    require account != user && account != currentContract;
    mathint userBalanceBefore = getSurplusCollShares(user);
    mathint accountBalanceBefore = getSurplusCollShares(account);

    increaseSurplusCollShares(e, user, amount);

    mathint userBalanceAfter = getSurplusCollShares(user);
    mathint accountBalanceAfter = getSurplusCollShares(account);

    assert userBalanceAfter == userBalanceBefore + amount;
    assert account != user => accountBalanceBefore == accountBalanceAfter;

}

rule claimSurplusCollSharesSpec(env e){
    address user;
    address account;
    uint256 amount;
    require amount >0;
    require account != user && account != currentContract;
    require user != currentContract;
    require e.msg.sender != user;


    mathint userBalanceBefore = getSurplusCollShares(e, user);
    mathint userCollBalanceBefore = collateral.balanceOf(user);
    mathint accountBalanceBefore = getSurplusCollShares(e, account);
    mathint accountCollBalanceBefore = collateral.balanceOf(account);
    mathint contractBalanceBefore = collateral.balanceOf(e, currentContract);
    mathint totalSharesBefore = getTotalSurplusCollShares(e);
    mathint userSharesBefore = collateral.sharesOf(e, user);
    mathint claimableColl = getSurplusCollShares(e, user);

    claimSurplusCollShares(e, user);

    mathint userBalanceAfter = getSurplusCollShares(e, user);
    mathint userCollBalanceAfter = collateral.balanceOf(user);
    mathint accountBalanceAfter = getSurplusCollShares(e, account);
    mathint accountCollBalanceAfter = collateral.balanceOf(account);
    mathint contractBalanceAfter = collateral.balanceOf(e, currentContract);
    mathint totalSharesAfter = getTotalSurplusCollShares(e);
    mathint userSharesAfter = collateral.sharesOf(e, user);


    assert userBalanceAfter == 0;
    assert userSharesAfter == userSharesBefore + claimableColl;
    //assert userCollBalanceAfter == userCollBalanceBefore + ;
    //assert contractBalanceAfter == contractBalanceBefore - ;
    //assert totalSharesAfter == totalSharesBefore - ;

    assert account != user => accountBalanceBefore == accountBalanceAfter;
    assert account != user => accountCollBalanceBefore == accountCollBalanceAfter;




}

rule increaseTotalSurplusCollSharesSpec(env e){
    uint256 amount;
    require amount > 0;

    mathint totalSharesBefore = getTotalSurplusCollShares(e);
    mathint balanceBefore = collateral.balanceOf(currentContract);

    increaseTotalSurplusCollShares(e, amount);

    mathint totalSharesAfter = getTotalSurplusCollShares(e);
    mathint balanceAfter = collateral.balanceOf(currentContract);

    assert totalSharesAfter == totalSharesBefore + amount;
    //assert balanceAfter == balanceBefore + amount;

    //assert totalSharesAfter == balanceAfter;


    
}
rule increaseTotalSurplusCollSharesIssueSpec(env e){
    uint256 amount;
    require amount > 0;

    mathint totalSharesBefore = getTotalSurplusCollShares(e);
    mathint balanceBefore = collateral.balanceOf(currentContract);

    increaseTotalSurplusCollShares(e, amount);

    mathint totalSharesAfter = getTotalSurplusCollShares(e);
    mathint balanceAfter = collateral.balanceOf(currentContract);

    assert totalSharesAfter == totalSharesBefore + amount;
    assert balanceAfter == balanceBefore + amount;

    assert totalSharesAfter == balanceAfter;


    
}


