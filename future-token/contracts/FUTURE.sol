// SPDX-License-Identifier: GPL-3.0
pragma solidity 0.8.0;

abstract contract IERC20 {

	function totalSupply() virtual public view returns (uint);
	function balanceOf(address tokenOwner) virtual public view returns (uint);
	function allowance(address tokenOwner, address spender) virtual public view returns (uint);
	function transfer(address to, uint tokens) virtual public returns (bool);
	function approve(address spender, uint tokens) virtual public returns (bool);
	function transferFrom(address from, address to, uint tokens) virtual public returns (bool);

	event Transfer(address indexed from, address indexed to, uint tokens);
	event Approval(address indexed tokenOwner, address indexed spender, uint tokens);
}


contract SafeMath {

	function safeAdd(uint256 a, uint256 b) internal pure returns (uint256) {
		uint256 c = a + b;
		require(c >= a, "SafeMath: addition overflow");
		return c;
	}

	function safeSub(uint256 a, uint256 b) internal pure returns (uint256) {
		require(b <= a, "SafeMath: subtraction overflow");
		uint256 c = a - b;
		return c;
	}
}


contract FUTURE is IERC20, SafeMath {
	string public name;
	string public symbol;
	uint8 public decimals; 

	uint256 public _totalSupply;
	address public owner;
	uint public _reward;

	mapping(address => uint) balances;
	mapping(address => mapping(address => uint)) allowed;

	constructor() payable {
		name = "FUTURE";
		symbol = "FTR";
		decimals = 8;
		owner = msg.sender;
		_totalSupply = 21000000 * 10 ** uint256(decimals);   // 24 decimals 
		_reward = 100;
		//balances[msg.sender] = _totalSupply;
		//emit Transfer(address(0), msg.sender, _totalSupply);
	}

	/**
	 * @dev allowance : Check approved balance
	 */
	function allowance(address tokenOwner, address spender) virtual override public view returns (uint remaining) {
		return allowed[tokenOwner][spender];
	}

	/**
	 * @dev approve : Approve token for spender
	 */ 
	function approve(address spender, uint tokens) virtual override public returns (bool success) {
		require(tokens >= 0, "Invalid value");
		allowed[msg.sender][spender] = tokens;
		emit Approval(msg.sender, spender, tokens);
		return true;
	}

	/**
	 * @dev transfer : Transfer token to another etherum address
	 */ 
	function transfer(address to, uint tokens) virtual override public returns (bool success) {
		require(to != address(0), "Null address");                                         
		require(tokens > 0, "Invalid Value");
		balances[msg.sender] = safeSub(balances[msg.sender], tokens);
		balances[to] = safeAdd(balances[to], tokens);
		emit Transfer(msg.sender, to, tokens);
		return true;
	}

	/**
	* @dev transferFrom : Transfer token after approval 
	*/ 
	function transferFrom(address from, address to, uint tokens) virtual override public returns (bool success) {
		require(to != address(0), "Null address");
		require(from != address(0), "Null address");
		require(tokens > 0, "Invalid value"); 
		require(tokens <= balances[from], "Insufficient balance");
		require(tokens <= allowed[from][msg.sender], "Insufficient allowance");
		balances[from] = safeSub(balances[from], tokens);
		allowed[from][msg.sender] = safeSub(allowed[from][msg.sender], tokens);
		balances[to] = safeAdd(balances[to], tokens);
		emit Transfer(from, to, tokens);
		return true;
	}

	/**
	* @dev totalSupply : Display total supply of token
	*/ 
	function totalSupply() virtual override public view returns (uint) {
		return _totalSupply;
	}

	/**
	* @dev balanceOf : Display token balance of given address
	*/ 
	function balanceOf(address tokenOwner) virtual override public view returns (uint balance) {
		return balances[tokenOwner];
	}

	/**
	* @dev sqrt : get the square root of a number using babylonian method
	*/ 
	function sqrt(int x) internal pure returns (int y) {
		int z = (x + 1) / 2;
		y = x;
		while (z < y) {
			y = z;
			z = (x / z + z) / 2;
		}
	}

	/**
	* @dev mint : To increase number of available tokens
	*/ 
	function mint(int[50] memory queryVec, int[50] memory answerVec) public returns (bool) {
		int dotProduct = 0;
		int sumQueryVec = 0;
		int sumAnswerVec = 0;
		int sameValues = 0;
		for(uint i = 0; i < 50; i++) {
			if (queryVec[i] == answerVec[i]) {
				sameValues += 1;
			}
			dotProduct = dotProduct + (queryVec[i] * answerVec[i]);
			sumQueryVec = sumQueryVec + (queryVec[i] ** 2);
			sumAnswerVec = sumAnswerVec + (answerVec[i] ** 2);
		}
		require(sameValues < 50, "Same input vectors.");
		int normQueryVec = sqrt(sumQueryVec);
		int normAnswerVec = sqrt(sumAnswerVec);
		require((normQueryVec + normAnswerVec) > 0, "Cannot divide by 0.");
		int cosSim = int(_reward) - ((dotProduct)/(normQueryVec + normAnswerVec));
		require(cosSim > 0, "Not successful answer.");
		uint _amount = uint(cosSim);
		balances[msg.sender] = safeAdd(balances[msg.sender], _amount);
		emit Transfer(address(0), msg.sender, _amount);
		return true;
	}

}
