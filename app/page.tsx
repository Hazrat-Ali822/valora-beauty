'use client'

import { useState } from 'react'
import { Heart, ShoppingCart, Search, User, ChevronLeft, ChevronRight, Star } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function Home() {
  const [cartCount, setCartCount] = useState(0)
  const [currentSlide, setCurrentSlide] = useState(0)
  const [wishlist, setWishlist] = useState<number[]>([])

  const heroSlides = [
    {
      id: 1,
      title: 'New Arrivals',
      subtitle: 'Discover our latest luxurious collections',
      image: 'linear-gradient(135deg, #FDF5F0 0%, #F5E6DC 100%)',
    },
    {
      id: 2,
      title: 'Signature Collection',
      subtitle: 'Timeless beauty essentials for the discerning',
      image: 'linear-gradient(135deg, #F5E6DC 0%, #EDD7C3 100%)',
    },
    {
      id: 3,
      title: 'Limited Edition',
      subtitle: 'Exclusive formulations available for a season only',
      image: 'linear-gradient(135deg, #EDD7C3 0%, #FDF5F0 100%)',
    },
  ]

  const collections = [
    { id: 1, name: 'Skincare', color: 'bg-[#FDF5F0]' },
    { id: 2, name: 'Makeup', color: 'bg-[#F5E6DC]' },
    { id: 3, name: 'Fragrance', color: 'bg-white' },
  ]

  const products = [
    { id: 1, name: 'Radiant Serum', price: '$85', image: 'bg-gradient-to-br from-[#F5E6DC] to-[#EDD7C3]' },
    { id: 2, name: 'Luxe Moisturizer', price: '$95', image: 'bg-gradient-to-br from-[#FDF5F0] to-[#F5E6DC]' },
    { id: 3, name: 'Velvet Lipstick', price: '$48', image: 'bg-gradient-to-br from-[#EDD7C3] to-[#FDF5F0]' },
    { id: 4, name: 'Golden Essence', price: '$120', image: 'bg-gradient-to-br from-[#F5E6DC] to-[#FDF5F0]' },
    { id: 5, name: 'Pearl Brightener', price: '$75', image: 'bg-gradient-to-br from-[#FDF5F0] to-[#EDD7C3]' },
    { id: 6, name: 'Silk Primer', price: '$55', image: 'bg-gradient-to-br from-[#F5E6DC] to-[#EDD7C3]' },
    { id: 7, name: 'Amber Fragrance', price: '$130', image: 'bg-gradient-to-br from-[#EDD7C3] to-[#F5E6DC]' },
    { id: 8, name: 'Crystal Cream', price: '$110', image: 'bg-gradient-to-br from-[#FDF5F0] to-[#F5E6DC]' },
  ]

  const toggleWishlist = (id: number) => {
    setWishlist(prev => 
      prev.includes(id) ? prev.filter(item => item !== id) : [...prev, id]
    )
  }

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % heroSlides.length)
  }

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + heroSlides.length) % heroSlides.length)
  }

  return (
    <main className="bg-white min-h-screen">
      {/* Fixed Navbar */}
      <nav className="fixed top-0 w-full bg-white border-b border-[#F0E6DC] z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          {/* Logo */}
          <div className="flex-shrink-0">
            <h1 className="font-serif text-2xl font-bold text-[#222222]">Valora Beauty</h1>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex gap-12 absolute left-1/2 transform -translate-x-1/2">
            <a href="#" className="font-serif text-sm text-[#222222] hover:text-[#A67C52] transition">Shop</a>
            <a href="#" className="font-serif text-sm text-[#222222] hover:text-[#A67C52] transition">Collections</a>
            <a href="#" className="font-serif text-sm text-[#222222] hover:text-[#A67C52] transition">About</a>
            <a href="#" className="font-serif text-sm text-[#222222] hover:text-[#A67C52] transition">Contact</a>
          </div>

          {/* Right Icons */}
          <div className="flex items-center gap-6">
            <button className="text-[#222222] hover:text-[#A67C52] transition p-2">
              <Search size={20} />
            </button>
            <button className="text-[#222222] hover:text-[#A67C52] transition p-2">
              <User size={20} />
            </button>
            <button className="text-[#222222] hover:text-[#A67C52] transition p-2">
              <Heart size={20} />
            </button>
            <button 
              className="relative p-2 text-[#222222] hover:text-[#A67C52] transition"
              onClick={() => setCartCount(prev => prev + 1)}
            >
              <ShoppingCart size={20} />
              {cartCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-[#A67C52] text-white text-xs w-5 h-5 rounded-full flex items-center justify-center">
                  {cartCount}
                </span>
              )}
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Slider */}
      <section className="mt-20 relative h-[600px] overflow-hidden bg-[#FDF5F0]">
        <div className="relative h-full flex items-center">
          {heroSlides.map((slide, index) => (
            <div
              key={slide.id}
              className={`absolute inset-0 transition-opacity duration-1000 ${
                index === currentSlide ? 'opacity-100' : 'opacity-0'
              }`}
              style={{ background: slide.image }}
            >
              <div className="h-full flex flex-col items-center justify-center text-center px-6">
                <h2 className="font-serif text-6xl font-bold text-[#222222] mb-4 max-w-3xl text-balance">
                  {slide.title}
                </h2>
                <p className="text-lg text-[#555555] mb-10 max-w-xl">
                  {slide.subtitle}
                </p>
                <Button className="bg-[#222222] text-white px-10 py-3 font-serif hover:bg-[#A67C52] transition">
                  Shop Now
                </Button>
              </div>
            </div>
          ))}
        </div>

        {/* Slider Controls */}
        <button
          onClick={prevSlide}
          className="absolute left-6 top-1/2 transform -translate-y-1/2 bg-white/80 hover:bg-white p-3 rounded-full z-10 transition"
        >
          <ChevronLeft size={24} className="text-[#222222]" />
        </button>
        <button
          onClick={nextSlide}
          className="absolute right-6 top-1/2 transform -translate-y-1/2 bg-white/80 hover:bg-white p-3 rounded-full z-10 transition"
        >
          <ChevronRight size={24} className="text-[#222222]" />
        </button>

        {/* Dots */}
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 flex gap-3 z-10">
          {heroSlides.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentSlide(index)}
              className={`w-2 h-2 rounded-full transition ${
                index === currentSlide ? 'bg-[#222222] w-8' : 'bg-[#222222]/30'
              }`}
            />
          ))}
        </div>
      </section>

      {/* Brand Trust Bar */}
      <section className="bg-white border-y border-[#F0E6DC] py-8">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex justify-around items-center gap-8 flex-wrap">
            {['Vogue', 'Harper\'s Bazaar', 'Elle', 'Cosmopolitan'].map((brand, idx) => (
              <div key={idx} className="text-center">
                <p className="text-sm font-serif text-[#222222] font-semibold tracking-wide">
                  AS FEATURED IN
                </p>
                <p className="text-lg font-serif text-[#A67C52] mt-1">{brand}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Collections */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <h3 className="font-serif text-4xl font-bold text-[#222222] text-center mb-16">
            Our Collections
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {collections.map((collection) => (
              <div
                key={collection.id}
                className={`${collection.color} p-12 rounded-lg flex flex-col items-center justify-center h-64 hover:shadow-lg transition cursor-pointer group`}
              >
                <h4 className="font-serif text-3xl font-bold text-[#222222] mb-4 group-hover:text-[#A67C52] transition">
                  {collection.name}
                </h4>
                <p className="text-sm text-[#555555] font-serif">Explore the range</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Luxury Product Grid */}
      <section className="py-20 bg-[#FDF5F0]">
        <div className="max-w-7xl mx-auto px-6">
          <h3 className="font-serif text-4xl font-bold text-[#222222] text-center mb-16">
            Luxury Products
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {products.map((product) => (
              <div key={product.id} className="group cursor-pointer">
                <div className={`${product.image} h-64 rounded-lg mb-6 flex items-center justify-center relative overflow-hidden`}>
                  <button
                    onClick={() => toggleWishlist(product.id)}
                    className="absolute top-4 right-4 bg-white p-2 rounded-full hover:bg-[#A67C52] transition z-10"
                  >
                    <Heart
                      size={18}
                      className={wishlist.includes(product.id) ? 'fill-[#A67C52] text-[#A67C52]' : 'text-[#222222]'}
                    />
                  </button>
                </div>
                <h4 className="font-serif text-lg font-semibold text-[#222222] mb-2">
                  {product.name}
                </h4>
                <div className="flex items-center justify-between mb-4">
                  <p className="font-serif text-xl font-bold text-[#A67C52]">
                    {product.price}
                  </p>
                  <div className="flex gap-1">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} size={14} className="fill-[#A67C52] text-[#A67C52]" />
                    ))}
                  </div>
                </div>
                <Button
                  onClick={() => setCartCount(prev => prev + 1)}
                  className="w-full bg-[#222222] text-white hover:bg-[#A67C52] transition font-serif"
                >
                  Add to Cart
                </Button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Newsletter Section */}
      <section className="py-20 bg-white border-y border-[#F0E6DC]">
        <div className="max-w-2xl mx-auto px-6 text-center">
          <h3 className="font-serif text-4xl font-bold text-[#222222] mb-6">
            Join Our Community
          </h3>
          <p className="text-[#555555] mb-10 font-serif text-lg">
            Receive exclusive offers and beauty tips delivered to your inbox.
          </p>
          <div className="flex gap-4 flex-col sm:flex-row">
            <input
              type="email"
              placeholder="Enter your email"
              className="flex-1 px-6 py-3 bg-[#FDF5F0] border border-[#E0D0C0] text-[#222222] font-serif placeholder:text-[#999999]"
            />
            <Button className="bg-[#222222] text-white hover:bg-[#A67C52] transition px-8 font-serif whitespace-nowrap">
              Subscribe
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-white border-t border-[#F0E6DC] py-16">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
            {/* About */}
            <div>
              <h5 className="font-serif text-lg font-bold text-[#222222] mb-6">About Valora</h5>
              <p className="text-sm text-[#555555] font-serif leading-relaxed">
                Crafted for the discerning, Valora Beauty represents the pinnacle of luxury skincare and cosmetics, blending timeless elegance with modern innovation.
              </p>
            </div>

            {/* Customer Service */}
            <div>
              <h5 className="font-serif text-lg font-bold text-[#222222] mb-6">Customer Service</h5>
              <ul className="space-y-3 text-sm text-[#555555] font-serif">
                <li><a href="#" className="hover:text-[#A67C52] transition">Contact Us</a></li>
                <li><a href="#" className="hover:text-[#A67C52] transition">Shipping Info</a></li>
                <li><a href="#" className="hover:text-[#A67C52] transition">Returns</a></li>
                <li><a href="#" className="hover:text-[#A67C52] transition">FAQ</a></li>
              </ul>
            </div>

            {/* Company */}
            <div>
              <h5 className="font-serif text-lg font-bold text-[#222222] mb-6">Company</h5>
              <ul className="space-y-3 text-sm text-[#555555] font-serif">
                <li><a href="#" className="hover:text-[#A67C52] transition">About Us</a></li>
                <li><a href="#" className="hover:text-[#A67C52] transition">Careers</a></li>
                <li><a href="#" className="hover:text-[#A67C52] transition">Press</a></li>
                <li><a href="#" className="hover:text-[#A67C52] transition">Blog</a></li>
              </ul>
            </div>

            {/* Social & Contact */}
            <div>
              <h5 className="font-serif text-lg font-bold text-[#222222] mb-6">Connect</h5>
              <div className="flex gap-4 mb-6">
                {['Instagram', 'Facebook', 'Twitter', 'Pinterest'].map((platform) => (
                  <a
                    key={platform}
                    href="#"
                    className="text-[#A67C52] hover:text-[#222222] transition font-serif text-sm"
                  >
                    {platform.charAt(0)}
                  </a>
                ))}
              </div>
              <p className="text-xs text-[#999999] font-serif">
                © 2025 Valora Beauty. All rights reserved.
              </p>
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="border-t border-[#F0E6DC] pt-8 flex flex-col md:flex-row justify-between items-center text-xs text-[#999999] font-serif gap-4">
            <p>Luxury Beauty Redefined</p>
            <div className="flex gap-6">
              <a href="#" className="hover:text-[#A67C52] transition">Privacy Policy</a>
              <a href="#" className="hover:text-[#A67C52] transition">Terms of Service</a>
            </div>
          </div>
        </div>
      </footer>
    </main>
  )
}
