'use strict';

// ---- Default Product Data ----
const PRODUCTS_DEFAULT = [
  { id:1,  name:'Rose Glow Vitamin C Serum',     category:'Skincare',  brand:'Lumière',   price:2499, stock:18, desc:'Brightening serum with 15% ascorbic acid.',      sku:'LMR-001', restock:5,  image:'' },
  { id:2,  name:'Velvet Matte Lipstick',          category:'Makeup',    brand:'NoirLab',   price:799,  stock:43, desc:'Long-lasting matte in 24 rich shades.',          sku:'NRL-002', restock:10, image:'' },
  { id:3,  name:'Midnight Bloom Parfum',          category:'Fragrance', brand:'Éclat',     price:5999, stock:9,  desc:'Oud, black rose and sandalwood.',                sku:'ECL-003', restock:3,  image:'' },
  { id:4,  name:'Argan Silk Hair Mask',           category:'Haircare',  brand:'SilkRoots', price:1299, stock:2,  desc:'Nourishing mask with argan oil and keratin.',    sku:'SLK-004', restock:5,  image:'' },
  { id:5,  name:'Crystal Dew Moisturiser',        category:'Skincare',  brand:'Lumière',   price:1899, stock:31, desc:'Lightweight gel moisturiser with hyaluronic acid.', sku:'LMR-005', restock:8, image:'' },
  { id:6,  name:'Satin Finish Foundation',        category:'Makeup',    brand:'NoirLab',   price:1599, stock:0,  desc:'Full-coverage foundation with SPF 25.',          sku:'NRL-006', restock:6,  image:'' },
  { id:7,  name:'Lavender Dream Body Oil',        category:'Wellness',  brand:'AuraBliss', price:999,  stock:15, desc:'Calming oil with lavender and chamomile.',       sku:'AUR-007', restock:5,  image:'' },
  { id:8,  name:'Peptide Eye Cream',              category:'Skincare',  brand:'Lumière',   price:3299, stock:7,  desc:'Triple-peptide technology for fine lines.',      sku:'LMR-008', restock:4,  image:'' },
  { id:9,  name:'Brow Sculptor Kit',              category:'Makeup',    brand:'NoirLab',   price:649,  stock:3,  desc:'Precision pencil and setting gel duo.',          sku:'NRL-009', restock:5,  image:'' },
  { id:10, name:'Citrus Burst Body Wash',         category:'Wellness',  brand:'AuraBliss', price:549,  stock:22, desc:'Energising gel with natural citrus extracts.',   sku:'AUR-010', restock:7,  image:'' },
  { id:11, name:'Amber Oud Eau de Parfum',        category:'Fragrance', brand:'Éclat',     price:7499, stock:0,  desc:'Oriental fragrance for lasting presence.',       sku:'ECL-011', restock:2,  image:'' },
  { id:12, name:'Castor Growth Hair Serum',       category:'Haircare',  brand:'SilkRoots', price:899,  stock:11, desc:'Scalp serum with cold-pressed castor oil.',      sku:'SLK-012', restock:5,  image:'' },
  { id:13, name:'Hyaluronic Glow Toner',          category:'Skincare',  brand:'Lumière',   price:1499, stock:4,  desc:'Plumping toner for deeper absorption.',          sku:'LMR-013', restock:6,  image:'' },
  { id:14, name:'Liquid Highlighter Drops',       category:'Makeup',    brand:'NoirLab',   price:1149, stock:19, desc:'Buildable glow drops for face and body.',        sku:'NRL-014', restock:5,  image:'' },
  { id:15, name:'Jasmine Neroli Eau de Toilette', category:'Fragrance', brand:'Éclat',     price:3999, stock:6,  desc:'Neroli, jasmine and white musk.',                sku:'ECL-015', restock:3,  image:'' },
];

// Category icons and colors
const ICONS = {
  Skincare:  'fa-droplet',
  Makeup:    'fa-wand-magic-sparkles',
  Fragrance: 'fa-wind',
  Haircare:  'fa-scissors',
  Wellness:  'fa-spa'
};

const COLORS = {
  Skincare:  '#3a9c8f',
  Makeup:    '#c9697a',
  Fragrance: '#8a6bc9',
  Haircare:  '#c9923a',
  Wellness:  '#4a9c6d'
};

const CATS = ['Skincare', 'Makeup', 'Fragrance', 'Haircare', 'Wellness'];
