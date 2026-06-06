# Real Garment Catalog

Place real product photos that you have permission to use in `data/catalog/images`.
Then add rows to `data/catalog/garments.csv`.

Example:

```csv
id,name,brand,category,image_path,image_url,source_url,license
blue-jacket,Blue Jacket,Acme,outerwear,images/blue-jacket.jpg,,https://example.com/products/blue-jacket,owned
```

Use either:

- `image_path`: a local file under `data/catalog/images`.
- `image_url`: a public image URL you own or have permission to use.

Do not add scraped or unlicensed brand imagery to this folder.
