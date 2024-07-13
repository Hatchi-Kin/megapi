# import os
# import tensorflow as tf

# from core.config import DEFAULT_SETTINGS
# from services.minio import load_model_from_minio, get_temp_file_from_minio

# # Disable GPU usage and suppress TensorFlow logging
# os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# # Enable eager execution for debugging
# tf.config.run_functions_eagerly(True)


# def extract_embeddings(file_path: str):
#     """Extract embeddings from an audio file."""
#     try:
#         # Load the OpenL3 model from MinIO
#         embedding_512_model = load_model_from_minio()
#         # full_path = f"{DEFAULT_SETTINGS.minio_openl3_bucket_name}/{file_path}"
#         temp_file_path = get_temp_file_from_minio(DEFAULT_SETTINGS.minio_openl3_bucket_name, file_path)

#         # Compute embeddings using the temporary file path
#         vector = embedding_512_model.compute(temp_file_path)
#         embedding = vector.mean(axis=0)

#         # Clean up the temporary file
#         os.unlink(temp_file_path)

#         return embedding.tolist()
    
#     except Exception as e:
#         raise Exception(f"File not found: {e}")