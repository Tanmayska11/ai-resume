'use client'

import { Auth0Provider } from '@auth0/auth0-react'

export default function AuthProvider({
  children,
}: {
  children: React.ReactNode
}) {

    
  return (
    <Auth0Provider
      domain={process.env.NEXT_PUBLIC_AUTH0_DOMAIN!}
      clientId={process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID!}
      authorizationParams={{
        redirect_uri: `${process.env.NEXT_PUBLIC_FRONTEND_URL}/admin`,
        audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE,
        scope: "openid profile email"
      }}
      
    >
    
      {children}
    </Auth0Provider>
  )
}
