import json
import logging
from typing import Optional, Dict, Any
from enum import Enum
from mcard.model.card import MCard
from mcard.engine.base import StorageEngine

logger = logging.getLogger(__name__)

class ExecutionStage(Enum):
    SPECIFICATION = "specification"
    IMPLEMENTATION = "implementation"
    EXPECTATION = "expectation"

class FunctionalStructure:
    def __init__(self, input_data: Dict[str, Any], process: Dict[str, Any], output: Dict[str, Any]):
        self.input_data = input_data
        self.process = process
        self.output = output
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "input": self.input_data,
            "activities": self.process,
            "output": self.output
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FunctionalStructure':
        return cls(
            input_data=data.get("input", {}),
            process=data.get("activities", {}),
            output=data.get("output", {})
        )

class FunctionalExecuter(StorageEngine):
    def __init__(self, base_engine: StorageEngine):
        self.base_engine = base_engine
        
    def add_execution(self, content: Dict[str, Any], stage: ExecutionStage) -> str:
        """Add execution content for a specific stage"""
        if stage == ExecutionStage.EXPECTATION:
            # For expectation, store accountability and references
            mcard_content = {
                "accountable_identity": content.get("accountable_identity", ""),
                "specification": content.get("specification", ""),
                "implementation": content.get("implementation", "")
            }
        else:
            # For specification or implementation, store functional structure
            func_struct = FunctionalStructure(
                input_data=content.get("input", {}),
                process=content.get("activities", {}),
                output=content.get("output", {})
            )
            mcard_content = func_struct.to_dict()
            
        mcard = MCard(json.dumps(mcard_content))
        return self.base_engine.add(mcard)
    
    def get_execution(self, hash_value: str) -> Optional[Dict[str, Any]]:
        """Retrieve execution content by hash"""
        mcard = self.base_engine.get(hash_value)
        if not mcard:
            return None
            
        try:
            return json.loads(mcard.content)
        except json.JSONDecodeError:
            logger.error(f"Failed to decode content for hash: {hash_value}")
            return None
            
    def verify_execution_chain(self, spec_hash: str, impl_hash: str, expect_hash: str) -> bool:
        """Verify the execution chain from specification through implementation to expectation"""
        spec = self.get_execution(spec_hash)
        impl = self.get_execution(impl_hash)
        expect = self.get_execution(expect_hash)
        
        if not all([spec, impl, expect]):
            return False
            
        # Verify expectation references match
        if not (
            expect.get("specification") == spec_hash and
            expect.get("implementation") == impl_hash
        ):
            return False
            
        return True
    
    # Implement required StorageEngine methods
    def add(self, card: MCard) -> str:
        return self.base_engine.add(card)
        
    def get(self, hash_value: str) -> Optional[MCard]:
        return self.base_engine.get(hash_value)
        
    def delete(self, hash_value: str) -> bool:
        return self.base_engine.delete(hash_value)