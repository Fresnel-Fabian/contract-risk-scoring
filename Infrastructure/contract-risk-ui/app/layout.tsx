import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Lex · Contract Risk Engine',
  description: 'AI-powered contract clause extraction and risk scoring',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
