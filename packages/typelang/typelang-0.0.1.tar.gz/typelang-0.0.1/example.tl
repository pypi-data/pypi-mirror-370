/** User model for the application */
@table("users")
type User = {
  /** Unique identifier */
  @primary
  id: string
  
  /** User's email address */
  @unique
  email: string
  
  /** User's display name */
  name: string
  
  /** User's age */
  age: int
  
  /** Optional phone number */
  phone?: string
  
  /** User tags */
  tags: string[]
  
  /** User settings */
  settings: Dict<string, any>
}

/** Product status enum */
type ProductStatus = "draft" | "published" | "out-of-stock"

/** Product model */
type Product = {
  id: string
  name: string
  price: float
  status: ProductStatus
  categories: string[]
}