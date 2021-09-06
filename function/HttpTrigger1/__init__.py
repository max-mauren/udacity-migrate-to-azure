import logging
import psycopg2
import azure.functions as func
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime
from psycopg2.extras import Json

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('id')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('id')

    if name:
            with psycopg2.connect("host=techconfdb.postgres.database.azure.com dbname=postgres user=tech_admin@techconfdb password=r74P@7Zg$76hV$9xg*f") as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT subject, message FROM public.notification WHERE id= %s;",(name,))

                    notifcation = cur.fetchone()
                    subject = notifcation[0]
                    message = notifcation[1]

                    # cur.close()
                    count = 0

                    sendgridapikey = ""

                    cur.execute("SELECT first_name, email FROM public.attendee")
                    for attendee in cur:
                        #send emails for each attendee
                        first_name=attendee[0]
                        email=attendee[1]

                        # if not sendgridapikey:
                        #     message = Mail(
                        #         from_email="max_mauren@hotmail.com",
                        #         to_emails=email,
                        #         subject=subject,
                        #         plain_text_content=message)

                        #     sg = SendGridAPIClient(sendgridapikey)
                        #     sg.send(message)

                        # count each one sent
                        count = count + 1

                    # update notification status
                    # statusmsg = str.join("Updated",str(count)," attendees")
                    completed_date = datetime.utcnow()
                    status = 'Notified {} attendees'.format(count)
                    
                    #params = [(status), ("completed_date":completed_date), ("id":id)]

                    #params = [Json({'status':status}, {'completed_date':completed_date}, {'id':id})]
                    params = (status,completed_date,name)
                    sql = """UPDATE public.notification SET status= %s, completed_date=%s WHERE id=%s"""
                    cur.execute(sql,params)
                    conn.commit()

                    #cur.close()


                #conn.close()
            return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
