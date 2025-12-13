'use client'

import React, { Component, ErrorInfo, ReactNode } from 'react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-6">
              <h2 className="text-2xl font-bold text-red-600 mb-4">Une erreur est survenue</h2>
              <p className="text-gray-700 mb-4">
                Désolé, une erreur inattendue s'est produite. Veuillez rafraîchir la page.
              </p>
              <button
                onClick={() => {
                  this.setState({ hasError: false, error: undefined })
                  window.location.reload()
                }}
                className="w-full bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-md transition-colors"
              >
                Rafraîchir la page
              </button>
            </div>
          </div>
        )
      )
    }

    return this.props.children
  }
}

