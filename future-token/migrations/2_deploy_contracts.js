var Contract = artifacts.require("FUTURE.sol");

module.exports = function(deployer) {
    deployer.deploy(Contract);
};
