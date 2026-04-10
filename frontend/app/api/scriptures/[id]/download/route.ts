import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  
  // Get filename from query params, or default to scripture.pdf
  const searchParams = request.nextUrl.searchParams;
  const filename = searchParams.get('filename') || 'scripture.pdf';
  
  try {
    // Fetch directly from FastAPI backend
    const baseUrl = process.env.API_URL && process.env.API_URL !== "undefined" ? process.env.API_URL : "https://sanatanagpt-api-gqx2jph6nq-uc.a.run.app";
    const res = await fetch(`${baseUrl}/api/scriptures/${id}/download`);
    
    if (!res.ok) {
      // Try to parse backend error detail if it exists
      let backendErr = 'Failed to fetch scripture';
      try {
        const errorData = await res.json();
        if (errorData.detail) backendErr = errorData.detail;
      } catch (e) {}

      return NextResponse.json({ error: backendErr }, { status: res.status });
    }

    // Proxy the stream perfectly to the browser, intercepting headers
    // We forcefully inject the filename into the Content-Disposition here so Chrome CANNOT ignore it
    const headers = new Headers(res.headers);
    headers.set('Content-Disposition', `attachment; filename="${filename}"`);
    headers.set('Content-Type', 'application/pdf');
    
    return new NextResponse(res.body, {
      headers,
      status: 200,
    });
  } catch (error) {
    console.error('Download proxy error:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
