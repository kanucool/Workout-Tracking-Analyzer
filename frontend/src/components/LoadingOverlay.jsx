
export default function LoadingOverlay({ loading }) {
    if (!loading) return null;

    return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      aria-modal="true"
      role="dialog"
      aria-label="Loading"
    >
      <div 
        className="h-12 w-12 animate-spin rounded-full border-4 border-solid border-white border-t-transparent"
        role="status"
      >
        <span className="sr-only">Loading...</span>
      </div>
    </div>
  );
}