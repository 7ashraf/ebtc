import "./sanity.spec";



methods {
    function balanceOf(address) external returns (uint256) envfree;
    function burn(address, uint256) external;
    function totalSupply() external  returns (uint256);
    function transfer(address, uint256) external returns (bool);
    function approve(address, uint256) external returns (bool);
    function increaseAllowance(address, uint256) external  returns (bool);
    function decreaseAllowance(address, uint256) external  returns (bool);
    function transferFrom(address, address, uint256) external returns (bool);
function permit(
        address owner,
        address spender,
        uint256 amount,
        uint256 deadline,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) external;
}



use rule sanity;



// This is an example of one of the simplest types of properties that we can implement
// unit-test like / integrity prtoperties, checking correctness of basic functionalities
rule mingIntegrity(env e) {
    address account;
    address user;
    uint256 amount;

    uint256 accountBalanceBefore = balanceOf(account);
    uint256 userBalanceBefore = balanceOf(user);

    mint(e, account, amount);

    uint256 accountBalanceAfter = balanceOf(account);
    uint256 userBalanceAfter = balanceOf(user);

    assert to_mathint(accountBalanceAfter) == accountBalanceBefore + amount;        // checking that account's balance was properly updated
    assert user != account => userBalanceBefore == userBalanceAfter;                // checking that other users' balances were not affected
}

rule burnSpec(env e){
    address account;
    address user;
    uint256 amount;

    require account != user;
    //states before
    mathint accountBalanceBefore = balanceOf(account);
    mathint userBalanceBefore = balanceOf(user);


    burn(e, account, amount);

    //states after
    mathint accountBalanceAfter = balanceOf(account);
    mathint userBalanceAfter = balanceOf(user);


    //asert states balances is changed
    assert accountBalanceAfter == accountBalanceBefore - amount;
    //should check for total supply decrease
    
    //other states not affected
    assert user != account => userBalanceBefore == userBalanceAfter;

}

rule transferSpec(env e){
    address sender;
    address recipient;
    address user;
    uint256 amount;
    
    mathint senderBalanceBefore = balanceOf(sender);
    mathint recipientBalanceBefore = balanceOf(recipient);
    mathint userBalanceBefore = balanceOf(user);
    require e.msg.sender == sender;
    transfer(e, recipient, amount);

    mathint senderBalanceAfter = balanceOf(sender);
    mathint recipientBalanceAfter = balanceOf(recipient);
    mathint userBalanceAfter = balanceOf(user);

    if(e.msg.sender != recipient){
        assert senderBalanceAfter == senderBalanceBefore - amount;
        assert recipientBalanceAfter == recipientBalanceBefore + amount;
    }else{
        assert senderBalanceAfter == senderBalanceBefore;
    }

    assert (user != sender && user != recipient) => userBalanceBefore == userBalanceAfter;
}

rule approveSpec(env e){
    address owner = e.msg.sender;
    address spender;
    address userA;
    address userB;
    uint256 amount;

    mathint userAllowanceBefore = allowance(e, userA, userB);

    require owner != spender;
    require amount > 0;

    approve(e, spender, amount);

    mathint allowanceAfter = allowance(e, owner, spender);

    assert assert_uint256(allowanceAfter) == amount;

    mathint userAllowanceAfter = allowance(e, userA, userB);


    assert userA != owner && userA != spender && userB != owner && userB != spender => userAllowanceBefore == userAllowanceAfter;

}

rule increaseAllowance(env e){
    address owner = e.msg.sender;
    address spender;
    address userA;
    address userB;
    uint256 amount;

    mathint userAllowanceBefore = allowance(e, userA, userB);
    mathint ownerAllowanceBefore = allowance(e, owner, spender);

    require owner != spender;

    increaseAllowance(e, spender, amount);

    mathint ownerAllowanceAfter = allowance(e, owner, spender);

    assert ownerAllowanceAfter == ownerAllowanceBefore + amount;

    mathint userAllowanceAfter = allowance(e, userA, userB);


    assert userA != owner && userA != spender && userB != owner && userB != spender => userAllowanceBefore == userAllowanceAfter;

}


rule decreaseAllowance(env e){
    address owner = e.msg.sender;
    address spender;
    address userA;
    address userB;
    uint256 amount;

    uint256 userAllowanceBefore = allowance(e, userA, userB);
    uint256 ownerAllowanceBefore = allowance(e, owner, spender);
    require owner != spender;

    decreaseAllowance(e, spender, amount);

    uint256 ownerAllowanceAfter = allowance(e, owner, spender);

    assert ownerAllowanceAfter == assert_uint256(ownerAllowanceBefore - amount);

    uint256 userAllowanceAfter = allowance(e, userA, userB);


    assert userA != owner && userA != spender && userB != owner && userB != spender => userAllowanceBefore == userAllowanceAfter;

} 

rule transferFromSpec(env e){

    address sender;
    address recipient;
    address accounts;
    uint256 amount;

    mathint senderBalanceBefore = balanceOf(sender);
    mathint recipientBalanceBefore = balanceOf(recipient);
    mathint accountsBalanceBefore = balanceOf(accounts);

    transferFrom(e, sender, recipient, amount);

    mathint senderBalanceAfter = balanceOf(sender);
    mathint recipientBalanceAfter = balanceOf(recipient);
    mathint accountsBalanceAfter = balanceOf(accounts);

    if(sender != recipient){
        assert senderBalanceAfter == senderBalanceBefore - amount;
        assert recipientBalanceAfter == recipientBalanceBefore + amount;
    }else{
        assert senderBalanceAfter == senderBalanceBefore;
    }

    assert (accounts != sender && accounts != recipient) => accountsBalanceAfter == accountsBalanceBefore;



}

rule permitSpec(env e){

    address owner;
    address spender;
    uint256 amount;
    uint256 deadline;
    uint8 v;
    bytes32 r;
    bytes32 s;
address userA;
    address userB;
    mathint userAllowanceBefore = allowance(e, userA, userB);

    require owner != spender;
    require amount > 0;

    permit(e, owner, spender, amount, deadline, v, r, s);

    mathint allowanceAfter = allowance(e, owner, spender);

    assert assert_uint256(allowanceAfter) == amount;

    mathint userAllowanceAfter = allowance(e, userA, userB);


    assert userA != owner && userA != spender && userB != owner && userB != spender => userAllowanceBefore == userAllowanceAfter;

}

