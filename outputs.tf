# http trigger url
output "function_url" {
  description = "processing function trigger url"
  value = module.functions.extract_transform_function_url
}