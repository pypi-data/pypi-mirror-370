"""
S3 Object Lock storage for EU compliance documents.
Ensures immutable storage with 7-year retention as required by EU regulations.
"""

import json
import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
import base64

try:
    import boto3
    from botocore.exceptions import ClientError
    S3_AVAILABLE = True
except ImportError:
    boto3 = None
    ClientError = None
    S3_AVAILABLE = False
    logging.warning("boto3 not installed - S3 storage disabled")

logger = logging.getLogger(__name__)


class ImmutableStorage:
    """S3 Object Lock storage for compliance documents."""
    
    def __init__(self, bucket_name: str = "lace-docs-prod", region: str = "eu-west-1"):
        """
        Initialize storage with S3 bucket configuration.
        
        Args:
            bucket_name: S3 bucket name (must have Object Lock enabled)
            region: AWS region (default: eu-west-1 for GDPR compliance)
        """
        self.bucket = bucket_name
        self.region = region
        self.kms_key = "alias/lace-signing"
        
        if S3_AVAILABLE:
            self.s3_client = boto3.client('s3', region_name=self.region)
            self.kms_client = boto3.client('kms', region_name=self.region)
            
            # Validate configuration on init
            self._validate_bucket_config()
        else:
            self.s3_client = None
            self.kms_client = None
            logger.warning("S3 storage not available - boto3 not installed")
    
    def _validate_bucket_config(self):
        """
        Validate S3 bucket has Object Lock and Versioning enabled.
        CRITICAL: These must be enabled for EU compliance.
        """
        if not self.s3_client:
            logger.warning("Cannot validate bucket - S3 client not available")
            return
        
        try:
            # Check bucket exists
            self.s3_client.head_bucket(Bucket=self.bucket)
            logger.info(f"✅ Bucket {self.bucket} exists")
            
            # Check Object Lock configuration
            try:
                lock_config = self.s3_client.get_object_lock_configuration(Bucket=self.bucket)
                if lock_config['ObjectLockConfiguration']['ObjectLockEnabled'] != 'Enabled':
                    raise ValueError(f"Object Lock not enabled on bucket {self.bucket}")
                logger.info("✅ Object Lock is enabled")
            except ClientError as e:
                if e.response['Error']['Code'] == 'ObjectLockConfigurationNotFoundError':
                    raise ValueError(f"Object Lock not configured on bucket {self.bucket}")
                raise
            
            # Check Versioning
            versioning = self.s3_client.get_bucket_versioning(Bucket=self.bucket)
            if versioning.get('Status') != 'Enabled':
                raise ValueError(f"Versioning not enabled on bucket {self.bucket}")
            logger.info("✅ Versioning is enabled")
            
            # Check KMS key (optional but recommended)
            try:
                key_info = self.kms_client.describe_key(KeyId=self.kms_key)
                if key_info['KeyMetadata']['KeyState'] != 'Enabled':
                    logger.warning(f"KMS key {self.kms_key} is not enabled")
                else:
                    logger.info(f"✅ KMS key {self.kms_key} is available")
            except ClientError:
                logger.warning(f"KMS key {self.kms_key} not found - signatures disabled")
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                raise ValueError(f"Bucket {self.bucket} does not exist")
            raise ValueError(f"Bucket validation failed: {e}")
        except Exception as e:
            logger.error(f"❌ Bucket configuration validation failed: {e}")
            raise
    
    def store_bundle(self, documents: Dict, metadata: Optional[Dict] = None) -> str:
        """
        Store document bundle with Object Lock and signatures.
        
        Args:
            documents: Dictionary containing all documents to store
            metadata: Optional metadata about the documents
            
        Returns:
            Bundle ID for retrieval
        """
        if not self.s3_client:
            logger.error("Cannot store bundle - S3 client not available")
            raise RuntimeError("S3 storage not configured")
        
        # Generate unique bundle ID
        bundle_id = self._generate_bundle_id(documents)
        
        # Create manifest with all documents and metadata
        manifest = self._create_manifest(documents, metadata, bundle_id)
        
        # Sign the manifest if KMS is available
        signature = self._sign_manifest(manifest)
        if signature:
            manifest['signature'] = signature
        
        # Store each document separately for clarity
        stored_files = []
        
        try:
            # Store main EU summary
            if 'eu_summary' in documents:
                key = f"{bundle_id}/eu_training_summary.json"
                self._store_document(key, documents['eu_summary'], "EU Training Summary")
                stored_files.append(key)
            
            # Store model card if present
            if 'model_card' in documents:
                key = f"{bundle_id}/model_card.md"
                self._store_document(key, documents['model_card'], "Model Card", content_type="text/markdown")
                stored_files.append(key)
            
            # Store copyright policy if present
            if 'copyright_policy' in documents:
                key = f"{bundle_id}/copyright_policy.md"
                self._store_document(key, documents['copyright_policy'], "Copyright Policy", content_type="text/markdown")
                stored_files.append(key)
            
            # Store HTML version if present
            if 'html_output' in documents:
                key = f"{bundle_id}/summary.html"
                self._store_document(key, documents['html_output'], "HTML Summary", content_type="text/html")
                stored_files.append(key)
            
            # Store the manifest
            manifest['stored_files'] = stored_files
            manifest_key = f"{bundle_id}/manifest.json"
            self._store_document(manifest_key, manifest, "Bundle Manifest")
            
            logger.info(f"✅ Document bundle stored successfully")
            logger.info(f"   Bundle ID: {bundle_id}")
            logger.info(f"   Files stored: {len(stored_files) + 1}")
            
            # Return bundle info
            return bundle_id
            
        except Exception as e:
            logger.error(f"Failed to store document bundle: {e}")
            raise
    
    def _generate_bundle_id(self, documents: Dict) -> str:
        """Generate unique, reproducible bundle ID."""
        # Create hash from document content
        content = json.dumps(documents, sort_keys=True)
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:12]
        
        # Add timestamp for uniqueness
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        return f"bundle_{timestamp}_{content_hash}"
    
    def _create_manifest(self, documents: Dict, metadata: Optional[Dict], bundle_id: str) -> Dict:
        """Create bundle manifest with provenance and metadata."""
        manifest = {
            'bundle_id': bundle_id,
            'created_at': datetime.now().isoformat(),
            'storage_version': '1.0.0',
            'retention': {
                'years': 7,
                'mode': 'COMPLIANCE',
                'reason': 'EU AI Act Article 53 requirement'
            },
            'documents': {
                'count': len(documents),
                'types': list(documents.keys())
            }
        }
        
        # Add metadata if provided
        if metadata:
            manifest['metadata'] = metadata
        
        # Add document hashes for integrity
        manifest['integrity'] = {}
        for doc_type, content in documents.items():
            if isinstance(content, dict):
                content_str = json.dumps(content, sort_keys=True)
            else:
                content_str = str(content)
            
            manifest['integrity'][doc_type] = {
                'sha256': hashlib.sha256(content_str.encode()).hexdigest(),
                'size': len(content_str)
            }
        
        return manifest
    
    def _sign_manifest(self, manifest: Dict) -> Optional[str]:
        """
        Sign manifest with KMS key for authenticity.
        
        Args:
            manifest: Manifest dictionary to sign
            
        Returns:
            Base64-encoded signature or None if KMS not available
        """
        if not self.kms_client:
            logger.warning("KMS client not available - skipping signature")
            return None
        
        try:
            # Create signing message
            message = json.dumps(manifest, sort_keys=True).encode('utf-8')
            message_hash = hashlib.sha256(message).digest()
            
            # Sign with KMS
            response = self.kms_client.sign(
                KeyId=self.kms_key,
                Message=message_hash,
                MessageType='DIGEST',
                SigningAlgorithm='RSASSA_PKCS1_V1_5_SHA_256'
            )
            
            # Return base64-encoded signature
            signature = base64.b64encode(response['Signature']).decode('utf-8')
            logger.info("✅ Manifest signed with KMS")
            return signature
            
        except Exception as e:
            logger.warning(f"Failed to sign manifest: {e}")
            return None
    
    def _store_document(
        self, 
        key: str, 
        content: Any, 
        description: str,
        content_type: str = "application/json"
    ):
        """
        Store individual document with Object Lock.
        
        Args:
            key: S3 object key
            content: Document content (dict or string)
            description: Human-readable description
            content_type: MIME type for the content
        """
        # Convert content to bytes
        if isinstance(content, dict):
            body = json.dumps(content, indent=2, ensure_ascii=False).encode('utf-8')
        elif isinstance(content, str):
            body = content.encode('utf-8')
        else:
            body = str(content).encode('utf-8')
        
        # Calculate retention date (7 years from now)
        retention_date = datetime.now() + timedelta(days=7*365)
        
        # Store object with metadata
        try:
            response = self.s3_client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=body,
                ContentType=content_type,
                ServerSideEncryption='AES256',
                Metadata={
                    'description': description,
                    'created_by': 'lace-wizard',
                    'created_at': datetime.now().isoformat()
                },
                ObjectLockMode='COMPLIANCE',
                ObjectLockRetainUntilDate=retention_date
            )
            
            logger.info(f"   ✅ Stored: {key} ({len(body)} bytes)")
            
            return response['VersionId']
            
        except ClientError as e:
            logger.error(f"Failed to store {key}: {e}")
            raise
    
    def retrieve_bundle(self, bundle_id: str) -> Dict[str, Any]:
        """
        Retrieve a stored document bundle.
        
        Args:
            bundle_id: Bundle ID returned from store_bundle
            
        Returns:
            Dictionary containing all documents and metadata
        """
        if not self.s3_client:
            raise RuntimeError("S3 storage not configured")
        
        try:
            # First get the manifest
            manifest_key = f"{bundle_id}/manifest.json"
            manifest_response = self.s3_client.get_object(
                Bucket=self.bucket,
                Key=manifest_key
            )
            manifest = json.loads(manifest_response['Body'].read())
            
            # Retrieve all documents
            documents = {}
            
            for file_key in manifest.get('stored_files', []):
                try:
                    response = self.s3_client.get_object(
                        Bucket=self.bucket,
                        Key=file_key
                    )
                    
                    content = response['Body'].read()
                    
                    # Determine document type from key
                    if file_key.endswith('.json'):
                        documents[Path(file_key).stem] = json.loads(content)
                    else:
                        documents[Path(file_key).stem] = content.decode('utf-8')
                        
                except ClientError as e:
                    logger.warning(f"Failed to retrieve {file_key}: {e}")
            
            return {
                'bundle_id': bundle_id,
                'manifest': manifest,
                'documents': documents
            }
            
        except ClientError as e:
            logger.error(f"Failed to retrieve bundle {bundle_id}: {e}")
            raise
    
    def list_bundles(self, prefix: str = "bundle_", max_results: int = 100) -> List[Dict]:
        """
        List stored document bundles.
        
        Args:
            prefix: Prefix to filter bundles
            max_results: Maximum number of results to return
            
        Returns:
            List of bundle metadata
        """
        if not self.s3_client:
            raise RuntimeError("S3 storage not configured")
        
        try:
            # List objects with prefix
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix,
                MaxKeys=max_results,
                Delimiter='/'
            )
            
            bundles = []
            
            # Extract bundle IDs from common prefixes
            for prefix_info in response.get('CommonPrefixes', []):
                bundle_id = prefix_info['Prefix'].rstrip('/')
                
                # Try to get manifest for metadata
                try:
                    manifest_response = self.s3_client.get_object(
                        Bucket=self.bucket,
                        Key=f"{bundle_id}/manifest.json"
                    )
                    manifest = json.loads(manifest_response['Body'].read())
                    
                    bundles.append({
                        'bundle_id': bundle_id,
                        'created_at': manifest.get('created_at'),
                        'document_count': manifest.get('documents', {}).get('count', 0),
                        'document_types': manifest.get('documents', {}).get('types', [])
                    })
                except:
                    # If manifest not found, just add basic info
                    bundles.append({
                        'bundle_id': bundle_id,
                        'created_at': 'unknown',
                        'document_count': 'unknown',
                        'document_types': []
                    })
            
            return bundles
            
        except ClientError as e:
            logger.error(f"Failed to list bundles: {e}")
            raise
    
    def verify_integrity(self, bundle_id: str) -> Dict[str, Any]:
        """
        Verify integrity of stored documents using manifest hashes.
        
        Args:
            bundle_id: Bundle ID to verify
            
        Returns:
            Verification results
        """
        if not self.s3_client:
            raise RuntimeError("S3 storage not configured")
        
        try:
            # Retrieve bundle
            bundle = self.retrieve_bundle(bundle_id)
            manifest = bundle['manifest']
            documents = bundle['documents']
            
            # Verify each document hash
            results = {
                'bundle_id': bundle_id,
                'verified_at': datetime.now().isoformat(),
                'documents': {}
            }
            
            for doc_type, expected_hash_info in manifest.get('integrity', {}).items():
                doc_name = doc_type.replace('_', ' ').title()
                
                if doc_type in documents:
                    # Calculate actual hash
                    content = documents[doc_type]
                    if isinstance(content, dict):
                        content_str = json.dumps(content, sort_keys=True)
                    else:
                        content_str = str(content)
                    
                    actual_hash = hashlib.sha256(content_str.encode()).hexdigest()
                    expected_hash = expected_hash_info['sha256']
                    
                    results['documents'][doc_type] = {
                        'valid': actual_hash == expected_hash,
                        'expected': expected_hash,
                        'actual': actual_hash
                    }
                else:
                    results['documents'][doc_type] = {
                        'valid': False,
                        'error': 'Document not found'
                    }
            
            # Overall result
            all_valid = all(doc.get('valid', False) for doc in results['documents'].values())
            results['valid'] = all_valid
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to verify bundle {bundle_id}: {e}")
            raise