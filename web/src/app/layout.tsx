import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'grimai',
  description: 'The AI that tells you the truth you don\'t want to hear.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
