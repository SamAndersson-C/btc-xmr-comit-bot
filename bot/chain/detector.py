from bitcoin.core import CTransaction
from bitcoin.core.script import CScript
from bitcoin.core.script import OP_EQUALVERIFY, OP_SHA256, OP_HASH160
from bitcoin.core.script import OP_CHECKLOCKTIMEVERIFY, OP_CHECKSEQUENCEVERIFY
from enum import Enum
from typing import Optional, List, Tuple

class SwapStep(Enum):
    LOCK = "LOCK"
    REDEEM = "REDEEM"
    REFUND = "REFUND"
    UNKNOWN = "UNKNOWN"

class HTLCDetector:
    """Detects HTLC (Hash Time-Locked Contract) scripts in Bitcoin transactions"""
    
    def is_htlc_like(self, witness_script: bytes) -> bool:
        """Check if a script looks like an HTLC"""
        try:
            ops = list(CScript(witness_script).raw_iter())
        except Exception:
            return False
        
        # Extract opcodes (integers)
        codes = [o for o in ops if isinstance(o, int)]
        
        # HTLC needs:
        # 1. A hash operation (SHA256 or HASH160)
        # 2. An equality check (EQUALVERIFY)
        # 3. A timelock (CLTV or CSV)
        has_hash = any(c in (OP_SHA256, OP_HASH160) for c in codes)
        has_eqv = OP_EQUALVERIFY in codes
        has_time = any(c in (OP_CHECKLOCKTIMEVERIFY, OP_CHECKSEQUENCEVERIFY) for c in codes)
        
        return has_hash and has_eqv and has_time
    
    def extract_witness_scripts(self, tx: CTransaction) -> List[Tuple[int, bytes]]:
        """Extract witness scripts from transaction inputs"""
        scripts = []
        
        for idx, txin in enumerate(tx.vin):
            if not hasattr(txin, 'scriptWitness') or not txin.scriptWitness:
                continue
            
            # In P2WSH, the last witness item is usually the script
            witness_items = txin.scriptWitness.stack
            if len(witness_items) > 0:
                potential_script = witness_items[-1]
                
                # Skip if too small
                if len(potential_script) > 40:
                    scripts.append((idx, bytes(potential_script)))
        
        return scripts
    
    def classify_step(self, tx: CTransaction) -> Tuple[SwapStep, Optional[bytes]]:
        """
        Classify what step of the swap this transaction represents
        Returns: (step, witness_script or None)
        """
        scripts = self.extract_witness_scripts(tx)
        
        for idx, script_bytes in scripts:
            if self.is_htlc_like(script_bytes):
                # Check if there's a preimage in the witness
                witness = tx.vin[idx].scriptWitness.stack
                
                # Look for 32-byte (SHA256) or 20-byte (HASH160) preimage
                has_preimage = any(
                    len(item) in (32, 20) for item in witness[:-1]  # Exclude the script itself
                )
                
                if has_preimage:
                    return (SwapStep.REDEEM, script_bytes)
                else:
                    return (SwapStep.REFUND, script_bytes)
        
        return (SwapStep.UNKNOWN, None)

if __name__ == "__main__":
    # Test with a dummy transaction
    print("HTLC Detector initialized! ✨")
    print("Ready to scan for atomic swaps...")