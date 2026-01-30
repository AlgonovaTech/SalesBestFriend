import { Component, type ReactNode } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error('ErrorBoundary caught:', error, info.componentStack)
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback

      return (
        <div className="flex min-h-[300px] items-center justify-center p-6">
          <Card className="max-w-md">
            <CardContent className="pt-6 text-center">
              <p className="text-sm font-medium">Something went wrong</p>
              <p className="mt-1 text-xs text-muted-foreground">
                {this.state.error?.message || 'An unexpected error occurred.'}
              </p>
              <Button
                variant="outline"
                size="sm"
                className="mt-4"
                onClick={() => this.setState({ hasError: false, error: null })}
              >
                Try again
              </Button>
            </CardContent>
          </Card>
        </div>
      )
    }

    return this.props.children
  }
}
