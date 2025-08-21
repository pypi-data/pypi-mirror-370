file_fragment = """
fragment FileFragment on File {
  id
  pk
  createdAt
  updatedAt
  createdBy
  location
  fileName
  fileSize
  fileChecksum
  isUploading
  isComplete
  partsDetails
  humanReadableMemorySize
  contents
}
"""
