import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Ratio Chart — Indian Market',
  description: 'Financial ratio charting for Indian market traders',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
