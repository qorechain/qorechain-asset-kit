// SPDX-License-Identifier: Apache-2.0

package assetkit

import "fmt"

// The five proposed modules. None of them exists on QoreChain.
const (
	ModuleAsset      = "x/asset"
	ModuleIdentity   = "x/identity"
	ModuleCompliance = "x/compliance"
	ModuleSettlement = "x/settlement"
	ModuleAttest     = "x/attest"
)

// CodeChainUpgradeRequired is the code of ChainUpgradeRequired.
const CodeChainUpgradeRequired = "CHAIN_UPGRADE_REQUIRED"

// ChainUpgradeRequired is returned by every call of the chain client: the module
// is a proposal, is not part of QoreChain, and needs a chain upgrade that is
// not scheduled.
type ChainUpgradeRequired struct {
	Module string
}

func (e *ChainUpgradeRequired) Error() string {
	return fmt.Sprintf("%s is a proposal and does not exist on QoreChain; it requires a chain upgrade that is not scheduled. "+
		"Use MockChain to build and test, or the EVM adapters (contracts/) for what works on QoreChain today.", e.Module)
}

// Code returns CHAIN_UPGRADE_REQUIRED.
func (e *ChainUpgradeRequired) Code() string { return CodeChainUpgradeRequired }

// MockChainError is a message refused by MockChain. Code is the name of the
// value in the module's proposed ErrorCode enum, for example
// ERROR_CODE_ADDRESS_FROZEN.
type MockChainError struct {
	Module  string
	Code    string
	Message string
}

func (e *MockChainError) Error() string {
	return fmt.Sprintf("%s: %s: %s", e.Module, e.Code, e.Message)
}

func fail(module, code, format string, args ...any) error {
	return &MockChainError{Module: module, Code: code, Message: fmt.Sprintf(format, args...)}
}
