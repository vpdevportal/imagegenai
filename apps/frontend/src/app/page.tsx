import { redirect } from 'next/navigation'

export default function Home() {
  // Redirect to the generate page as the default
  redirect('/generate')
}
