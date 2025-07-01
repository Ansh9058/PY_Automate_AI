$headers = @{
    "accept" = "application/json"
    "Content-Type" = "application/json"
}

$body = @{
    url = "https://www.amazon.com/s?k=laptop"
    selectors = @{
        product_container = 'div[data-component-type="s-search-result"]'
        title = "h2 a span"
        price = ".a-price .a-offscreen"
        image = "img.s-image"
        description = ".a-size-base"
    }
} | ConvertTo-Json

$response = Invoke-RestMethod `
    -Uri "http://127.0.0.1:8080/api/v1/rpa/scrape-products" `
    -Method Post `
    -Headers $headers `
    -Body $body

Write-Host "Status: $($response.status)"
if ($response.products) {
    Write-Host "Found $($response.products.Count) products"
    foreach ($product in $response.products) {
        Write-Host "`nProduct:"
        Write-Host "Title: $($product.title)"
        Write-Host "Price: $($product.price)"
        Write-Host "Image URL: $($product.image_url)"
        Write-Host "-" * 50
    }
}
