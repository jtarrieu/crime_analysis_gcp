# http trigger url
output "function_url" {
  description = "processing function trigger url"
  value = module.functions.start_processing_pipeline_url
}